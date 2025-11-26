from django.core.management.base import BaseCommand
from userbaseapp.models import Bet, BulkBetAction

class Command(BaseCommand):
    help = 'Delete all bets and bulk actions from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without prompting',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n⚠️  WARNING: This will delete ALL bets and bulk actions!\n'))
        
        # Count existing records
        bet_count = Bet.objects.count()
        bulk_action_count = BulkBetAction.objects.count()
        
        self.stdout.write(f'Found:')
        self.stdout.write(f'  - {bet_count} bets')
        self.stdout.write(f'  - {bulk_action_count} bulk actions\n')
        
        if not options['confirm']:
            confirm = input('Are you sure you want to delete all data? Type "yes" to confirm: ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('❌ Deletion cancelled\n'))
                return
        
        # Delete all bets
        self.stdout.write('🗑️  Deleting all bets...')
        deleted_bets = Bet.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'   ✅ Deleted {deleted_bets[0]} bets'))
        
        # Delete all bulk actions
        self.stdout.write('🗑️  Deleting all bulk actions...')
        deleted_actions = BulkBetAction.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'   ✅ Deleted {deleted_actions[0]} bulk actions'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ All bets deleted successfully!\n'))
