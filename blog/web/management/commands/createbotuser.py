from django.core.management import BaseCommand

from web.models import Profile


class Command(BaseCommand):
    help = 'Create bot user'

    def handle(self, *args, **options):
        botuser = Profile.objects.create_user(username='botuser', password='botuser',
                                               email='botuser@gmail.com')
        botuser.save()
        self.stdout.write( self.style.SUCCESS('Added botuser'))