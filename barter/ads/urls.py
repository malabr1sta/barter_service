from django.urls import path

from ads import views as ads_views

app_name = "ads"

urlpatterns = [
    path("", ads_views.index_page, name="index_page"),
    path("ad_create/", ads_views.ad_create, name="ad_create"),
    path("ad_update/<int:pk>/", ads_views.ad_update, name="ad_update"),
    path("ad_delete/<int:pk>/", ads_views.ad_soft_delete, name="ad_delete"),
    path(
        "proposal_create/<int:ad_receiver_pk>/",
        ads_views.proposal_create,
        name="prop_create"
    ),
]
