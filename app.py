!pip install transformers==4.29.2
!pip install accelerate==0.19.0
!pip install torch==2.0.0
!pip install einops==0.6.1
!pip install flask
!pip install pytelegrambotapi
!pip install python-dotenv
!pip install requests
!pip install twilio

from flask import Flask,redirect,url_for,render_template,request
from twilio.rest import Client

from chat import get_response

#for emotion analysis
import joblib
loaded_model = joblib.load('/content/emotion_model.joblib')
#sentiment scores are as followed
'''Anger-0
  Disgust-1
  Fear-2
  Guilty-3
  Joy-4
  Love-5
  Sadness-6
  Shame-7
  surprise-8'''

#comment the telebot part if you want to just use the chatbot in web
#to use telebot open telegram and serach hearky_bot or head over to t.me/hearky_bot on your browser
import telebot
bot=telebot.TeleBot('6447345913:AAHAJCE94pJ3weuLKV2gqdf7T6UiIp6IAW0')


@bot.message_handler(commands=['ai','info'])
def ai_handler(message):
  if message.text=='/ai':
    bot.reply_to(message,'Be clear pal. What do you want talk about? 🙂 ')
  if message.text=='/info':
    bot.reply_to(message,'Sup!!🙂 i am hearky , your Ai telebot created by Master Atulya.')
    bot.reply_to(message,'Ask me anything (use /ai followed by your text), will try my best to answer it ✊')
  else:
    refine_message=message.text.replace('/ai','')
    emotion_num=loaded_model.predict([refine_message]) #predicts the sentiment number

    response=f"""
    {get_response(refine_message)}
    """
    senti_msg=''
    if(emotion_num==0):
      senti_msg="you seem angry. I know the whole world sucks sometimes,but we gotta keep our cool and move on."

    elif(emotion_num==2):
      senti_msg="I have texted the authorities and your family memebers, until they reach out to you just keep calm and keep it low"

    elif (emotion_num==6):
      senti_msg="We all have our lows and highs. These times test us and we need to keep our hearts strong and face it with all of our might.Just believe and everything's gonna be fine ✊"

    elif (emotion_num==7 or emotion_num==3):
      senti_msg="There are times when we regret the choices we make, but even then we have our options, whether to keep on thinking about the mistakes or take a choice to somehow mend it. The choices we make at this point makes all the difference my friend :"

    bot.reply_to(message,response)
    bot.reply_to(message,senti_msg)

if __name__=='__main__':
  print('bot is running')
  bot.polling()

#comment this part if u want to use telebot
#a public url will be generated on which our web app will be rendered locally(when using google colab)
from google.colab.output import eval_js
print(eval_js("google.colab.kernel.proxyPort(5000)"))


app=Flask(__name__,template_folder='/content/templates')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['msg']
        predicted_label = loaded_model.predict([user_input])

        got_num=0
        num=user_input[0:13] #number on which message needs to be sent.
        num_without_plus=user_input[1:13]
        user_name=user_input[14:]
        print(num)
        print(user_name)
        if(num_without_plus.isnumeric()): #to check the validity of number if provided
          got_num=1;
          emergency_msg=f'your friend {user_name} seems to be in trouble. Please reach out to him -- hearky'

          account_sid = 'ACfb7b5de7cd4934430469c62b5ebf98cc'
          auth_token = 'e67df05c397e2851b7c06c5e4c7e0ec2'
          client = Client(account_sid, auth_token)
          message = client.messages.create(
            from_='+16184378302',
            body=emergency_msg,
            to=num
          )
          if(message.sid):
            print("message sent")

          return render_template('emergency.html')

        else:
          text=get_response(user_input)
          print(predicted_label)
          return render_template('msg.html',botResponse=text,emotion_num=predicted_label)
    return render_template('index.html')


if __name__=="__main__":
  app.run()
