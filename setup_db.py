import os
import shutil

from src.app.dao import post_dao as pd
from src.app.dao import routine_dao as rd
from src.app.dao import social_media_dao as smd
from src.app.utils import db_utils

def setup_dbs():
  print('Setting up databases...')
  os.system('python manage.py db init')
  os.system('python manage.py db migrate')
  os.system('python manage.py db upgrade')
  print('Finished setting up databases...')

def delete_migrations():
  try:
    shutil.rmtree('migrations')
    os.system('export PGPASSWORD={}; psql --user={} --host={} {} '
              .format(os.environ['DB_PASSWORD'], os.environ['DB_USERNAME'],
                      os.environ['DB_HOST'], os.environ['DB_NAME'])
              + '-c \'drop table alembic_version\'')
    print('Migrations folder deleted...')

  except OSError:
    print('No migrations folder to delete...')

def init_data():
  image_prefix = 'https://raw.githubusercontent.com/cuappdev/assets/master/uplift/influencers/'
  print('Adding posts to db...')
  _, juan_garcia_post = pd.create_post(
    biography=('My name is Juan Garcia and I\'m a junior studying Operations Research and Information Engineering '
               'with a minor in Business. I\'m from Edinburg, Texas which is a border town alongside the Rio Grande '
               'River which separates Texas and Mexico. I began my lifting career the summer after high school when '
               'I was here at Cornell participating in the Prefreshman Summer Program.(shoutout to my 2016 PSP class!)'
               ' Outside of classes and lifting, I enjoy playing a variety of sports, more importantly basketball, '
               'hiking when it\'s a beautiful day outside, playing video games, and collaborating with others on '
               'ideas that can potentially make positive impacts on communities.'),
    college='Engineering',
    expertises='Weightlifting',
    large_picture=image_prefix+'juan.png',
    name='Juan Garcia',
    quote='',
    small_picture=''
  )

  _, juan_garcia_cardio = rd.create_routine(
      category='cardio',
      post_id=juan_garcia_post.id,
      steps=('If you\'re going for distance, start off at a distance that you are comfortable with(i.e. 1 mile) '
             'and add .25-.5 miles to it with every week that you go to challenge yourself to reach your hidden '
             'potential. On the other hand, if you\'re going for speed, do short bursts(10-20 seconds) of '
             'sprinting on the treadmill followed by 45 seconds to a minute of rest and repeat 8-10 times.'),
      title='Juan Garcia Cardio'
  )

  _, juan_garcia_strength = rd.create_routine(
      category='strength',
      post_id=juan_garcia_post.id,
      steps=('Know what your one rep max is for compound movements which include Bench Press, Squats, and Deadlifts '
             'to name a few. From there, begin performing these movements ranging from 3 reps to 5 reps for 3 to 5 '
             'sets with a weight that is 70-75% of your one rep max. In addition, work on accessories that are needed '
             'for each compound movement(i.e. Chest, shoulders and triceps for Bench Press). Never do the same '
             'exercises when you go to the gym, best thing for muscle growth/strength is shocking your muscles with '
             'different routines or training methods. For example, one training method that I like to do is '
             'dropsetting, which consists of starting at a particular weight and performing reps with it until failure'
             ', followed by dropping the weight by 5-10 pounds and repeating this cycle of reaching failure until you '
             'get to a weight that stops challenging you.'),
      title='Juan Garcia Strength'
  )

  _, juan_garcia_mindfulness = rd.create_routine(
      category='mindfulness',
      post_id=juan_garcia_post.id,
      steps=('I\'d recommend either reading a book for 10 min a day or going on a walk for 10-15 without music '
             'playing.'),
      title='Juan Garcia Mindfulness'
  )

  _, juan_garcia_sm = smd.create_social_media(
    facebook='https://www.facebook.com/profile.php?id=100010308969934',
    instagram='https://www.instagram.com/jv_gar1012/',
    post_id=juan_garcia_post.id
  )

  juan_garcia_post.routines.append(juan_garcia_cardio)
  juan_garcia_post.routines.append(juan_garcia_strength)
  juan_garcia_post.routines.append(juan_garcia_mindfulness)
  juan_garcia_post.social_media.append(juan_garcia_sm)

  _, madeline_ugarte_post = pd.create_post(
    biography=('I\'m a National Academy of Sports Medicine Certified Personal Trainer and Performance Enhancement '
      'Specialist (NASM-CPT, PES), and I\'m a certified instructor in Spinning, SpinPower, TRX, Power HIIT and '
      'Shockwave. Other than that, I\'m a proud Chicago native and a senior at Cornell. Can\'t wait to see you '
      'in a class!'), 
    college='Arts & Sciences',
    expertises='Spinning, Weightlifting, Strength & Conditioning',
    large_picture=image_prefix+'madeline.jpg',
    name='Madeline Ugarte',
    quote='',
    small_picture=''
  )

  _, madeline_ugarte_cardio = rd.create_routine(
    category='cardio',
    post_id=madeline_ugarte_post.id,
    steps=('You\'re already probably getting your steps in without even realizing it (you can thank all the Cornell '
      'hills for that!). So to step it up a notch I\'d recommend a group fitness class like Spinning for beginners '
      'so they can increase their cardio performance with some guidance!'),
    title='Madeline Ugarte Cardio'
  )

  _, madeline_ugarte_strength = rd.create_routine(
    category='strength',
    post_id=madeline_ugarte_post.id,
    steps=('Start small, stay consistent and pick something you actually like! My advice would be to pick a skill '
      'that you\'d like to improve and incorporate it consistently at the end of your workouts or throughout the '
      'day. When I first started out I really wanted to get better at pushups so I always ended my workouts with 10 '
      'pushups, now it\'s part of my warm up instead!'),
    title='Madeline Ugarte Strength'
  )

  _, madeline_ugarte_mindfulness = rd.create_routine(
    category='mindfulness',
    post_id=madeline_ugarte_post.id,
    steps=('Give yourself 30 minutes a day to do something that makes you happy. I wake up earlier than I need to '
      'every morning for an oat milk latte and 30 minutes to lightly stretch and go through my Instagram feed--just '
      'to have some time to myself!'),
    title='Madeline Ugarte Mindfulness'
  )

  _, madeline_ugarte_sm = smd.create_social_media(
    instagram='https://www.instagram.com/trainwithmadeline/',
    post_id=madeline_ugarte_post.id
  )

  madeline_ugarte_post.routines.append(madeline_ugarte_cardio)
  madeline_ugarte_post.routines.append(madeline_ugarte_strength)
  madeline_ugarte_post.routines.append(madeline_ugarte_mindfulness)
  madeline_ugarte_post.social_media.append(madeline_ugarte_sm)

  _, starks_twins_post = pd.create_post(
    biography=('We\'re twin powerbuilders: people who lift to get stronger and look better. As students, we\'re '
      'computational biology majors who intend to attend graduate school in bioinformatics, computational biology, '
      'or computer science.'), 
    college='Arts & Sciences',
    expertises='Powerlifting and Bodybuilding',
    large_picture=image_prefix+'starks.png',
    name='Austin and Justin Starks', 
    quote='',
    small_picture=''
  )

  _, starks_twins_cardio = rd.create_routine(
    category='cardio',
    post_id=starks_twins_post.id,
    steps=('Walk to class everyday. Unless it\'s sub-zero outside, walking to class on a campus like Cornell will '
      'get thousands of steps per day. Plus, with all of the slopes and hills, you are bound to get an effective '
      'cardio workout everyday.'),
    title='Starks Twins Cardio'
  )

  _, starks_twins_strength = rd.create_routine(
    category='strength',
    post_id=starks_twins_post.id,
    steps=('Go to the gym, and go consistently. Even if you plan to go twice per week, it is important to establish '
      'the routine. Going consistently is what will get you to your goals.'),
    title='Starks Twins Strength'
  )

  _, starks_twins_mindfulness = rd.create_routine(
    category='mindfulness',
    post_id=starks_twins_post.id,
    steps=('Take time for yourself everyday. It is important to relax your mind and brain and do something you '
      'enjoy, even if it is just for 20 minutes a day.'),
    title='Starks Twins Mindfulness'
  )

  _, starks_twins_sm = smd.create_social_media(
    instagram='https://www.instagram.com/starkstwins/',
    post_id=starks_twins_post.id
  )

  starks_twins_post.routines.append(starks_twins_cardio)
  starks_twins_post.routines.append(starks_twins_strength)
  starks_twins_post.routines.append(starks_twins_mindfulness)
  starks_twins_post.social_media.append(starks_twins_sm)

  _, cleo_kyriakides_post = pd.create_post(
    biography=('I\'m a long distance runner who got hooked onto CrossFit along the way! I love feeling strong and '
      'sharing my knowledge to help people reach their goals. I\'m also the 2018-19 Fitness Club prez and a member '
      'of Track Club!'), 
    college='Engineering',
    expertises='Running, Olympic lifting, CrossFit',
    large_picture=image_prefix+'cleo.png',
    name='Cleo Kyriakides',
    quote='',
    small_picture=''
  )

  _, cleo_kyriakides_cardio = rd.create_routine(
    category='cardio',
    post_id=cleo_kyriakides_post.id,
    steps=('Start out with small, achievable goals. Start by running up to a mile at a time every time you run, and '
      'don\'t increase by more than a mile each week. Listen to your body, get the right shoes, and make sure '
      'someone checks your form!'),
    title='Cleo Kyriakides Cardio'
  )

  _, cleo_kyriakides_strength = rd.create_routine(
    category='strength',
    post_id=cleo_kyriakides_post.id,
    steps=('First of all, form is EVERYTHING. Work with someone who can spot you for the movements as you start. '
      'Muscle fatigue each time is not desired, so start by doing small rep/low weight circuits of simple movements '
      '(back squats, presses, deadlifts) 3x a week, increasing weight 5-10lbs each week.'),
    title='Cleo Kyriakides Strength'
  )

  _, cleo_kyriakides_mindfulness = rd.create_routine(
    category='mindfulness',
    post_id=cleo_kyriakides_post.id,
    steps=('I am an avid knitter and I do yoga regularly. Find something that relaxes you that isn\'t physically '
      'taxing and turn it into a habit! Additionally, take time to reflect at the beginning or end of each day, '
      'actively watching thoughts pass through your head without dwelling on them.'),
    title='Cleo Kyriakides Mindfulness'
  )

  _, cleo_kyriakides_sm = smd.create_social_media(
    instagram='https://instagram.com/fitnessbycleo',
    post_id=cleo_kyriakides_post.id
  )

  cleo_kyriakides_post.routines.append(cleo_kyriakides_cardio)
  cleo_kyriakides_post.routines.append(cleo_kyriakides_strength)
  cleo_kyriakides_post.routines.append(cleo_kyriakides_mindfulness)
  cleo_kyriakides_post.social_media.append(cleo_kyriakides_sm)

  _, clarie_ng_post = pd.create_post(
    biography=('A proponent of every body is beautiful. I like to tailor workouts for myself because each person has '
      'different gene, muscle insertions, and body proportions. There\'s no \'end\' to a fitness journey in my '
      'opinion but a lifestyle to celebrate the amazing capabilities of our body. I believe our body was made to move '
      'and feel incredible. I hope to set people on the right path towards loving themselves and exercise.'),
    college='CALS',
    expertises='Weightlifting, circuits, diet, body building, aesthetics',
    large_picture=image_prefix+'clarie.png',
    name='Clarie Ng',
    quote='',
    small_picture=''
  )

  _, clarie_ng_cardio = rd.create_routine(
    category='cardio',
    post_id=clarie_ng_post.id,
    steps=('10,000 Steps a day or incorporate walking from place to places. I rather someone be active the entire '
    'day than run for 30 minutes and sit on the couch for the rest of the day. Cardio should not be a chore but '
    'assimilated into your life. (unless you have some speed or endurance goal or have a time crunch during exam '
    'season)'),
    title='Clarie Ng Cardio'
  )

  _, clarie_ng_strength = rd.create_routine(
    category='strength',
    post_id=clarie_ng_post.id,
    steps=('PROPER form is king! Never lift something heavier for the sake of ego. You can make better muscle gains'
    ' by going lighter but doing the full range of motion. Body weights are fantastic and should be the goal of '
    'everyone: imagine being able to bench heavy and yet can\'t even do a push up. That\'s lame. Being able to '
    'carry your own weight is a sign of balance!'),
    title='Clarie Ng Strength'
  )

  _, clarie_ng_mindfulness = rd.create_routine(
    category='mindfulness',
    post_id=clarie_ng_post.id,
    steps=('Do something for yourself. Chase your own best version of you and not how you think other people will '
    'like you to look. I don\'t meditate but I heard many friends who high encourage it. Yoga is great for '
    'practicing mindfulness.'),
    title='Clarie Ng Mindfulness'
  )

  _, clarie_ng_sm = smd.create_social_media(
    instagram='https://www.instagram.com/thenvironmentalistbodybuilder/',
    post_id=clarie_ng_post.id
  )

  clarie_ng_post.routines.append(clarie_ng_cardio)
  clarie_ng_post.routines.append(clarie_ng_strength)
  clarie_ng_post.routines.append(clarie_ng_mindfulness)
  clarie_ng_post.social_media.append(clarie_ng_sm)

  _, mark_rittiboon_post = pd.create_post(
    biography=('I used to be a competitive strength athlete participating in powerlifting and strongman competitions.'
    ' However, I\'ve transitioned into combat sports ~ recently completing a fighting camp in Phuket Thailand!'), 
    college='Johnson School of Business / Hotelie',
    expertises='Weightlifting',
    large_picture=image_prefix+'mark.png',
    name='Mark Rittiboon',
    quote='',
    small_picture=''
  )

  _, mark_rittiboon_cardio = rd.create_routine(
    category='cardio',
    post_id=mark_rittiboon_post.id,
    steps=('I don\'t enjoy running and Ithaca is really cold so I don\'t do it haha... I find swimming to be really'
      ' fun and effective. For me, it\'s also the best form of active recovery! '),
    title='Mark Rittiboon Cardio'
  )

  _, mark_rittiboon_strength = rd.create_routine(
    category='strength',
    post_id=mark_rittiboon_post.id,
    steps=('I think everyone looking to build strength should focus on compound lifts (Squats, Deadlifts, Bench, etc)'
    '. A 5x5 beginner program is a good start!'),
    title='Mark Rittiboon Strength'
  )

  _, mark_rittiboon_mindfulness = rd.create_routine(
    category='mindfulness',
    post_id=mark_rittiboon_post.id,
    steps=('I love to cook! Nothing like Spotify\'s \'cooking music\' playlist and eggs in the morning :) '
      'https://open.spotify.com/user/123149640/playlist/2xhceuxK7ERTQnBCfIEt1y?si=ZvmFtf3mQvevS5zz75eNKA'),
    title='Mark Rittiboon Mindfulness'
  )

  _, mark_rittiboon_sm = smd.create_social_media(
    facebook='https://www.facebook.com/mark.rittiboon',
    post_id=mark_rittiboon_post.id
  )

  mark_rittiboon_post.routines.append(mark_rittiboon_cardio)
  mark_rittiboon_post.routines.append(mark_rittiboon_strength)
  mark_rittiboon_post.routines.append(mark_rittiboon_mindfulness)
  mark_rittiboon_post.social_media.append(mark_rittiboon_sm)

  db_utils.commit_model(juan_garcia_cardio)
  db_utils.commit_model(juan_garcia_strength)
  db_utils.commit_model(juan_garcia_mindfulness)
  db_utils.commit_model(juan_garcia_post)

  db_utils.commit_model(madeline_ugarte_cardio)
  db_utils.commit_model(madeline_ugarte_strength)
  db_utils.commit_model(madeline_ugarte_mindfulness)
  db_utils.commit_model(madeline_ugarte_post)

  db_utils.commit_model(starks_twins_cardio)
  db_utils.commit_model(starks_twins_strength)
  db_utils.commit_model(starks_twins_mindfulness)
  db_utils.commit_model(starks_twins_post)

  db_utils.commit_model(cleo_kyriakides_cardio)
  db_utils.commit_model(cleo_kyriakides_strength)
  db_utils.commit_model(cleo_kyriakides_mindfulness)
  db_utils.commit_model(cleo_kyriakides_post)

  db_utils.commit_model(clarie_ng_cardio)
  db_utils.commit_model(clarie_ng_strength)
  db_utils.commit_model(clarie_ng_mindfulness)
  db_utils.commit_model(clarie_ng_post)

  db_utils.commit_model(mark_rittiboon_cardio)
  db_utils.commit_model(mark_rittiboon_strength)
  db_utils.commit_model(mark_rittiboon_mindfulness)
  db_utils.commit_model(mark_rittiboon_post)



if __name__ == '__main__':
  delete_migrations()
  setup_dbs()
  init_data()
