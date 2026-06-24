from django.core.management.base import BaseCommand
from workouts.models import Exercise


class Command(BaseCommand):
    help = 'Update exercise video URLs with valid YouTube links'

    def handle(self, *args, **options):
        video_map = {
            # === CALISTHENICS / ADVANCED ===
            'Muscle Ups': 'https://www.youtube.com/embed/_eQ2gw_Gg5Y',
            'Muscle-Ups': 'https://www.youtube.com/embed/_eQ2gw_Gg5Y',
            'Muscle Up': 'https://www.youtube.com/embed/_eQ2gw_Gg5Y',
            'Handstand Pushups': 'https://www.youtube.com/embed/zA2nuzsSDKQ',
            'Handstand Push-Ups': 'https://www.youtube.com/embed/zA2nuzsSDKQ',
            'Handstand Pushup': 'https://www.youtube.com/embed/zA2nuzsSDKQ',
            'Planche': 'https://www.youtube.com/embed/fcN37TxBE_s',
            'Planche Pushups': 'https://www.youtube.com/embed/fcN37TxBE_s',
            'Front Lever': 'https://www.youtube.com/embed/8sX80YJLkA8',
            'Front Lever Rows': 'https://www.youtube.com/embed/8sX80YJLkA8',
            'Back Lever': 'https://www.youtube.com/embed/8yIEhe2lgOo',
            'L-Sit': 'https://www.youtube.com/embed/1vhC5KjfBZ4',
            'L-Sit Pull Ups': 'https://www.youtube.com/embed/1vhC5KjfBZ4',
            'Human Flag': 'https://www.youtube.com/embed/4mn-2rVc7I0',
            'Pistol Squat': 'https://www.youtube.com/embed/sZfNXl8uDFs',
            'Pistol Squats': 'https://www.youtube.com/embed/sZfNXl8uDFs',
            'Dragon Flag': 'https://www.youtube.com/embed/ah6d8Jt58d0',
            'One Arm Chin Up': 'https://www.youtube.com/embed/5c4jq7iL_H0',
            'Clap Push Ups': 'https://www.youtube.com/embed/z9mhO63ltG4',
            '360 Pull Up': 'https://www.youtube.com/embed/6Rf7UB8EmuI',

            # === POWERLIFTING / STRENGTH ===
            'Barbell Squat': 'https://www.youtube.com/embed/ultWZbUMPL8',
            'Deadlift': 'https://www.youtube.com/embed/op9kVnSso6Q',
            'Deadlifts': 'https://www.youtube.com/embed/op9kVnSso6Q',
            'Bench Press': 'https://www.youtube.com/embed/gRVjAtPip0Y',
            'Overhead Press': 'https://www.youtube.com/embed/2IN5g1lVx-A',
            'Barbell Row': 'https://www.youtube.com/embed/dH2aBN4hzrA',
            'Dumbbell Rows': 'https://www.youtube.com/embed/dH2aBN4hzrA',
            'Pull Ups': 'https://www.youtube.com/embed/eGo4IYlbE5g',
            'Dips': 'https://www.youtube.com/embed/2z8lSnHhBvE',
            'Lunges': 'https://www.youtube.com/embed/QOVaHvg-QVg',
            'Walking Lunges': 'https://www.youtube.com/embed/QOVaHvg-QVg',
            'Plank': 'https://www.youtube.com/embed/pSHjTRCQxIw',

            # === BEGINNER ===
            'Bodyweight Squat': 'https://www.youtube.com/embed/BF9HvRv7YwE',
            'Bodyweight Squats': 'https://www.youtube.com/embed/BF9HvRv7YwE',
            'Push Ups': 'https://www.youtube.com/embed/OD0U2r6B0Ig',
            'Push-Ups': 'https://www.youtube.com/embed/OD0U2r6B0Ig',
            'Glute Bridge': 'https://www.youtube.com/embed/8n1hxVv-hpE',
            'Bird Dog': 'https://www.youtube.com/embed/vk6l06y_gZQ',
            'Dead Bug': 'https://www.youtube.com/embed/FqKjtsjYScM',
            'Knee Push Ups': 'https://www.youtube.com/embed/JWD_BF7P3i8',
            'Wall Push Ups': 'https://www.youtube.com/embed/7nU3uGrcLaM',

            # === UPPER BODY ===
            'Dumbbell Shoulder Press': 'https://www.youtube.com/embed/Adk3W2kY6qE',
            'Lat Pulldown': 'https://www.youtube.com/embed/CAwf7n6Luic',
            'Cable Row': 'https://www.youtube.com/embed/9dDNDo3T8rU',
            'Dumbbell Curl': 'https://www.youtube.com/embed/9G9WozMnF50',
            'Tricep Pushdown': 'https://www.youtube.com/embed/kiPUkBwEOM0',
            'Face Pull': 'https://www.youtube.com/embed/HZ3Hh5gS3KI',
            'Lateral Raise': 'https://www.youtube.com/embed/3VcKaXpzqRo',
            'Front Raise': 'https://www.youtube.com/embed/tO6E9zQDcTo',
            'Reverse Fly': 'https://www.youtube.com/embed/KWQkR5Wyc_M',
            'Skull Crushers': 'https://www.youtube.com/embed/dT2Wl4lGt6o',
            'Hammer Curls': 'https://www.youtube.com/embed/zC3nLlEvin4',
            'Incline Dumbbell Press': 'https://www.youtube.com/embed/2bbf9pAOlEQ',
            'Decline Bench Press': 'https://www.youtube.com/embed/LI1VZ5cNz28',
            'Pec Deck Fly': 'https://www.youtube.com/embed/KZ4ElE1KqNc',
            'Cable Crossovers': 'https://www.youtube.com/embed/taI4XduLpTk',

            # === LOWER BODY ===
            'Romanian Deadlift': 'https://www.youtube.com/embed/JC6L69SjfMc',
            'Leg Press': 'https://www.youtube.com/embed/IztE7t55O9M',
            'Leg Curl': 'https://www.youtube.com/embed/1Tq3QdILLpc',
            'Leg Extension': 'https://www.youtube.com/embed/AmCqjGRS6m0',
            'Calf Raise': 'https://www.youtube.com/embed/uSgYlX3MPGQ',
            'Bulgarian Split Squat': 'https://www.youtube.com/embed/2C-uNgKwCc4',
            'Hip Thrust': 'https://www.youtube.com/embed/SEdqd1nBQ-w',
            'Box Squat': 'https://www.youtube.com/embed/-TDF8bB0eMk',
            'Goblet Squat': 'https://www.youtube.com/embed/MeIu13k7T8I',
            'Sumo Deadlift': 'https://www.youtube.com/embed/SslOcI8klD8',
            'Stiff Leg Deadlift': 'https://www.youtube.com/embed/JC6L69SjfMc',

            # === CARDIO & HIIT ===
            'Jumping Jacks': 'https://www.youtube.com/embed/c4DAnQ0iJmM',
            'Burpees': 'https://www.youtube.com/embed/TU8QYVW0gDU',
            'Mountain Climbers': 'https://www.youtube.com/embed/nmwgirgXLYM',
            'High Knees': 'https://www.youtube.com/embed/ycM-TLe_wio',
            'Jump Squats': 'https://www.youtube.com/embed/9_fbS80gP7I',
            'Box Jumps': 'https://www.youtube.com/embed/52r_Ul5k03Q',
            'Battle Ropes': 'https://www.youtube.com/embed/cB9nYfQLwF0',
            'Kettlebell Swings': 'https://www.youtube.com/embed/ys8l5_GmBsE',
            'Skipping Rope': 'https://www.youtube.com/embed/DwzLi_d-lsM',
            'Stair Climber': 'https://www.youtube.com/embed/qgALZ9H5yI4',

            # === CORE ===
            'Crunches': 'https://www.youtube.com/embed/Xyd_fa5zoEU',
            'Russian Twists': 'https://www.youtube.com/embed/wkD8rjkopT8',
            'Leg Raises': 'https://www.youtube.com/embed/JB2oyawG9KI',
            'Bicycle Crunches': 'https://www.youtube.com/embed/9FGilxCbdz8',
            'Side Plank': 'https://www.youtube.com/embed/3SGx1yA_WWg',
            'V-Ups': 'https://www.youtube.com/embed/eNda9soy9jQ',
            'Flutter Kicks': 'https://www.youtube.com/embed/M3FJkC-7U_Q',
            'Sit Ups': 'https://www.youtube.com/embed/jDwoBqPH0vE',
            'Reverse Crunches': 'https://www.youtube.com/embed/fkAaee5l1L4',
            'Toe Touches': 'https://www.youtube.com/embed/TM8BrpSCWII',
            'Hanging Leg Raises': 'https://www.youtube.com/embed/JB2oyawG9KI',
            'Ab Wheel Rollouts': 'https://www.youtube.com/embed/UP3OSIeF_s8',

            # === STRETCHING / MOBILITY ===
            'Hamstring Stretch': 'https://www.youtube.com/embed/5T5-BRw_3qk',
            'Quad Stretch': 'https://www.youtube.com/embed/8lHcJJZ5yXU',
            'Chest Stretch': 'https://www.youtube.com/embed/Zr6SOVv0cLw',
            'Shoulder Stretch': 'https://www.youtube.com/embed/H3L61lh8GYk',
            'Hip Flexor Stretch': 'https://www.youtube.com/embed/VnAqD_mJ4Lk',
            'Pigeon Pose': 'https://www.youtube.com/embed/Mr6StKk93o0',
            'Cat Cow Stretch': 'https://www.youtube.com/embed/kqnua4rD8R8',
            'Child Pose': 'https://www.youtube.com/embed/Ga5P5t04TH0',
            'Downward Dog': 'https://www.youtube.com/embed/j7Tn8jCjUgs',
            'Cobra Stretch': 'https://www.youtube.com/embed/JDcdhTuycOI',
            'Butterfly Stretch': 'https://www.youtube.com/embed/58YJZCd7AsU',
            'Triceps Stretch': 'https://www.youtube.com/embed/Zr6SOVv0cLw',
            'Neck Stretch': 'https://www.youtube.com/embed/6Rf7UB8EmuI',
        }

        updated_count = 0
        not_found = []

        for name, url in video_map.items():
            exercises = Exercise.objects.filter(name__iexact=name)

            if not exercises.exists():
                alternate_name = name.replace('-', ' ').strip()
                if alternate_name != name:
                    exercises = Exercise.objects.filter(name__iexact=alternate_name)

            if not exercises.exists():
                exercises = Exercise.objects.filter(name__icontains=name)
                if exercises.count() > 1:
                    self.stdout.write(self.style.WARNING(
                        f"Ambiguous match for '{name}' ({exercises.count()} exercises); skipping."))
                    not_found.append(name)
                    continue

            if exercises.exists():
                for exercise in exercises:
                    exercise.video_url = url
                    exercise.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated: {exercise.name}"))
            else:
                not_found.append(name)
                self.stdout.write(self.style.WARNING(f"Not found: {name}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {updated_count} exercises"))
        if not_found:
            self.stdout.write(self.style.WARNING(f"Exercises not found: {len(not_found)}"))
            for name in not_found:
                self.stdout.write(f"  - {name}")
