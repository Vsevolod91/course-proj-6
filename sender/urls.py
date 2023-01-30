from django.urls import path
from sender.views import*
from sender.apps import SenderConfig

app_name = SenderConfig.name

urlpatterns = [
    path('', LoginUser.as_view(), name='login'),
    path('register/', RegisterUser.as_view(), name='registration'),
    path('logout/', logout_user, name='logout'),
    path('profile/', ListAndCreateConfigMailing.as_view(), name='profile'),
    path('profile/mailing-<int:pk>', ConfigMailingDetailView.as_view(), name='mailing_detail'),
    path('profile/update-mailing-<int:pk>', ConfigMailingUpdateView.as_view(), name='update_mailing'),
    path('profile/delete-mailing-<int:pk>', ConfigMailingDeleteView.as_view(), name='delete_mailing'),
    path('profile/update-letter-<int:pk>', LetterMailingUpdateView.as_view(), name='update_letter'),
    path('profile/delete-letter-<int:pk>', LetterMailingDeleteView.as_view(), name='delete_letter'),
    path('trials/', TryMailingListView.as_view(), name='trials')
]