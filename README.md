# Better Heroku Scheduler

## The feature I wish Heroku Scheduler already had

Often than I would like to admit, I find myself struggling to manage my Heroku free hours. Even though I already have extended to the 1000 hours with the credit card, it's excruciating to see all my precious hours slipping through my fingers.

And if it wasn't already bad, just wait: it happens that almost every single dyno that I used was idle most of the time. In other words, my hours counter was going down and I wasn't using them at all.

At that point I decided that it was enough, and commited myself to find a solution. At first glance, the best approach seemed to be to just turn the damn thing off when I didn't need it to work. The closest thing that seemed to fit my needs (for free, I must remember you - after all, the whole point of this was to save money) was the standard [Heroku Scheduler](https://devcenter.heroku.com/articles/scheduler). And it is indeed an OK solution; if you have, for example, a bot that tweets the weather every day, it's completely nonsense to have a dyno working 24 hours per day. It's much better to just schedule the task and run an [one-off dyno](https://devcenter.heroku.com/articles/one-off-dynos) when needed.

However, if you have for example, a [Telegram Bot](https://core.telegram.org/bots) that you want to work from 7am to 11pm, you won't be able to do much with Heroku Scheduler. After all, it's in their docs:

> Scheduled jobs are meant to execute short running tasks or enqueue longer running tasks into a background job queue. Anything that takes longer than a couple of minutes to complete should use a worker dyno to run.
>
> _[Heroku Scheduler docs about long-running jobs](https://devcenter.heroku.com/articles/scheduler#long-running-jobs)_

So, how to proceed? Well, I don't know if it's the best approach, but I took the **enqueue longer running tasks** to the letter, and set up a script that would turn on and off my dynos. Since I think more people can make use of this, I'm making it available here. Nothing fancy to be honest, and you could just like me spend a day implementing this yourself. But if it's already done, why not right?

## How it works?

As I said, it's nothing fancy. It's just a [Selenium](https://www.selenium.dev/) script that opens up your Heroku dashboard and turn dynos on and off. At first I tried to reverse engineer the networking and find the request that did that - with no success. I don't know if I wasn't motivated enough (but probably, to be honest. If I said I spent more than five minutes trying to find something I would be lying).

## How to use it?

It's fairly straight forward. In abstract, what you need to do is:

- Clone this repository and deploy it to Heroku
- Add some environment variables to set everything up
- Paste some buildpacks links to make Selenium work
- Add the [Heroku Scheduler](https://elements.heroku.com/addons/scheduler) add-on to your app and set the activation and deactivation times to your app _(worth mentioning that to do this you need to have a credit card linked to your account - I know, what a tragedy)_

### Create a Heroku app

Assuming that you already have [Git](https://git-scm.com/) installed, you can just clone the repository to your local machine.

```sh
  git clone https://github.com/arthurvergacas/better-heroku-scheduler.git
  cd better-heroku-scheduler
```

After that, it's time to create an app on Heroku. You can do this easily using the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli), and after loggin in, execute the following:

```sh
  heroku create better-scheduler
```

This will create a new app called `better-scheduler`, but you can call it whatever you want.

Now, you can open the browser and see your brand new app using:

```sh
  heroku open
```

Alternatively, you can just go to your Heroku dashboard and find it there.

### Setting everything up

After you created your app and everything seems OK, it's time to configure the environment. To do this, click on your app, and then go to the **Settings** tab. There, you must do two things:

#### Create the environment variables

Below App Information, you will find the field **Config Vars**. Click to reveal the vars and add the following:

- **KEY:** CHROMEDRIVER_PATH | **VALUE:** /app/.chromedriver/bin/chromedriver
- **KEY:** GOOGLE_CHROME_BIN | **VALUE:** /app/.apt/usr/bin/google-chrome
- **KEY:** HEROKU_CREDENTIALS_EMAIL | **VALUE:** _The email used to log in your Heroku Account_
- **KEY:** HEROKU_CREDENTIALS_PASSWORD | **VALUE:** _The password used to log in your Heroku Account_

> Two things are worth remembering here:
>
> - Inserting your private credentials here is your own responsibility. If you have any doubts of where or how they are used, the code is available for you to check for yourself. **Never enter your credentials in random software that you found in the internet and that you don't understand**
>
> - If you have Two Factor Authentication this script might not be useful for you. After all, TFW is used exactly to prevent things that aren't you (like this script) from accessing your account.

#### Configure the buildpacks

After configuring all the environment variables, you need to configure the buildpacks. They are the drivers that Selenium uses to navigate to Heroku.

To add the buildpacks, go to **Settings**, and below **Config Vars** you will find the field **Buildpacks**. Click on _Add buildpack_ and paste the following links:

- Google Chrome Buildpack: <https://github.com/heroku/heroku-buildpack-google-chrome>
- Google Chrome Driver Buildpack: <https://github.com/heroku/heroku-buildpack-chromedriver>

_Don't worry if Heroku tells you that the buildpack will be used in the next time the app is deployed; we will handle this in a second._

### Setting the scheduler

After all variables have been set and the buildpacks been added, it's time to configure the scheduler.

First, go to your app, and in the tab **Resources** add the add-on [Heroku Scheduler](https://elements.heroku.com/addons/scheduler). Once it's added, click on it to open the add-on dashboard.

In the dashboard, click on **Create job**. A modal will appear so you can configure the task. Here is where you can define when the dyno is activated and deactivated. Let's walk through an example to demonstrate it better:

Suppose you have the Telegram Bot that I talked about earlier, and you want it to work from 7am to 11pm. To configure this, choose _Every day at..._ in the drop menu and set the time to _07:00 PM_ **(Pay attention to the timezone! You might need to take it in consideration).**

Now, in the **Run Command** field, you need to tell the scheduler what task you want it to execute at that time. In our case, we type the following:

```sh
  python activate_dyno.py <name_of_your_app> <process_of_your_dyno>
```

Here, the `name_of_your_app` is the name of the app that you want to control. In our case, this might be something like `telegram-bot`.

`process_of_your_dyno`, on the other hand, is the command that the dyno executes. For example, in our Telegram Bot we might have the worker dyno `python bot.py`. It's important to notice the space between words here. To handle this, you can use "double quotes" or back\ slashes.

The final example would be something like:

```sh
  python activate_dyno.py telegram-bot "python bot.py"
```

When everything is ready, you can click **Save Job** to add the job to the scheduler.

Adding the job to **deactivate** the dyno is similar. The main difference is the name of the script that will be executed.

```sh
  python deactivate_dyno.py <name_of_your_app> <process_of_your_dyno>
```

Which to our bot would be

```sh
  python deactivate_dyno.py telegram-bot "python bot.py"
```

### Deploying your application

After the app is created, the variables are setted and the tasks are defined, it's time to deploy the scheduler. To do this, go to the folder where the code of this repository is located and execute the following:

```sh
  git push heroku master
```

When you typed `heroku create` in the beggining, it also created a git remote called `heroku` that you can use to push your code.

And ta-da! Easy as that, your dynos are now properly managed by the scheduler. Just as a reminder, you can always add more dynos or apps to the scheduler to control.

Enjoy your hours not being completely wasted! 🎉
