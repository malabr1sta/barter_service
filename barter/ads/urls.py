from django.urls import path

from ads import views as ads_views

app_name = "ads"

urlpatterns = [
    path("", ads_views.index_page, name="index_page"),
    path("ad-create/", ads_views.ad_create, name="ad_create"),
    path("ad-update/<int:pk>/", ads_views.ad_update, name="ad_update"),
    path("ad-delete/<int:pk>/", ads_views.ad_soft_delete, name="ad_delete"),
    path(
        "proposal-create/<int:ad_receiver_pk>/",
        ads_views.proposal_create,
        name="prop_create"
    ),
    path("proposals-list", ads_views.proposals_list, name="proposals_list"),
    path(
        "proposal-update/<int:pk>/",
        ads_views.proposal_update,
        name="prop_update"
    ),
]
