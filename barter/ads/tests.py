import tempfile
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from ads import models as ads_models

User = get_user_model()


class AdModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='pass'
        )
        self.ad = ads_models.Ad.objects.create(
            user=self.user,
            title='Test Ad',
            description='Test Description',
            category=ads_models.Ad.BOOKS,
            condition=ads_models.Ad.NEW
        )

    def test_create_ad(self):
        """Проверяет создание объявления."""
        self.assertEqual(ads_models.Ad.objects.count(), 1)
        self.assertEqual(self.ad.title, 'Test Ad')

    def test_update_ad(self):
        """Проверяет редактирование объявления."""
        self.ad.title = 'Updated Title'
        self.ad.save()
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.title, 'Updated Title')

    def test_soft_delete_ad(self):
        """Проверяет мягкое удаление объявления (deleted=True)."""
        self.ad.deleted = True
        self.ad.save()
        self.assertFalse(
            ads_models.Ad.active_objects.filter(pk=self.ad.pk).exists())

    def test_search_ad(self):
        """Проверяет поиск объявления по заголовку."""
        ads = ads_models.Ad.active_objects.filter(title__icontains='Test')
        self.assertIn(self.ad, ads)

class ExchangeProposalModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', password='pass'
        )
        self.user2 = User.objects.create_user(
            username='user2', password='pass'
        )
        self.ad1 = ads_models.Ad.objects.create(
            user=self.user1,
            title='Ad1',
            description='desc1',
            category=ads_models.Ad.BOOKS,
            condition=ads_models.Ad.NEW
        )
        self.ad2 = ads_models.Ad.objects.create(
            user=self.user2,
            title='Ad2',
            description='desc2',
            category=ads_models.Ad.CLOTHES,
            condition=ads_models.Ad.USED
        )
        self.proposal = ads_models.ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment_sender='Let\'s exchange'
        )

    def test_create_proposal(self):
        """Проверяет создание предложения обмена."""
        self.assertEqual(ads_models.ExchangeProposal.objects.count(), 1)
        self.assertEqual(
            self.proposal.status, ads_models.ExchangeProposal.PENDING)

    def test_update_proposal_status(self):
        """Проверяет изменение статуса предложения обмена."""
        self.proposal.status = ads_models.ExchangeProposal.ACCEPTED
        self.proposal.save()
        self.proposal.refresh_from_db()
        self.assertEqual(
            self.proposal.status, ads_models.ExchangeProposal.ACCEPTED)

    def test_get_user_proposals(self):
        """Проверяет получение предложений пользователя."""
        proposals = ads_models.ExchangeProposal.get_user_proposals(self.user1)
        self.assertIn(self.proposal, proposals)

class AdViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='pass'
        )
        self.client.login(username='testuser', password='pass')
        self.ad = ads_models.Ad.objects.create(
            user=self.user,
            title='Test Ad',
            description='Test Description',
            category=ads_models.Ad.BOOKS,
            condition=ads_models.Ad.NEW
        )

    def test_index_page(self):
        """Проверяет отображение главной страницы объявлений."""
        response = self.client.get(reverse('ads:index_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Ad')

    def test_ad_create(self):
        """Проверяет создание объявления через view."""
        with tempfile.NamedTemporaryFile(suffix=".jpg") as img:
            response = self.client.post(reverse('ads:ad_create'), {
                'title': 'New Ad',
                'description': 'desc',
                'category': ads_models.Ad.BOOKS,
                'condition': ads_models.Ad.NEW,
            })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ads_models.Ad.objects.filter(title='New Ad').exists())

    def test_ad_update(self):
        """Проверяет редактирование объявления через view."""
        response = self.client.post(
            reverse('ads:ad_update', args=[self.ad.pk]), {
            'title': 'Changed',
            'description': 'desc',
            'category': ads_models.Ad.BOOKS,
            'condition': ads_models.Ad.NEW,
        })
        self.assertEqual(response.status_code, 302)
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.title, 'Changed')

    def test_ad_soft_delete(self):
        """Проверяет мягкое удаление объявления через view."""
        response = self.client.post(
            reverse('ads:ad_delete', args=[self.ad.pk]))
        self.assertEqual(response.status_code, 302)
        self.ad.refresh_from_db()
        self.assertTrue(self.ad.deleted)


class ExchangeProposalViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.client.login(username='user1', password='pass')
        self.ad1 = ads_models.Ad.objects.create(
            user=self.user1,
            title='Ad1',
            description='desc1',
            category=ads_models.Ad.BOOKS,
            condition=ads_models.Ad.NEW
        )
        self.ad2 = ads_models.Ad.objects.create(
            user=self.user2,
            title='Ad2',
            description='desc2',
            category=ads_models.Ad.CLOTHES,
            condition=ads_models.Ad.USED
        )

    def test_proposal_create_view(self):
        """Проверяет создание предложения обмена через view."""
        response = self.client.post(
            reverse('ads:prop_create', args=[self.ad2.pk]),
            {
                'ad_sender': self.ad1.pk,
                'comment_sender': 'Test proposal'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ads_models.ExchangeProposal.objects.filter(
                ad_sender=self.ad1, ad_receiver=self.ad2
            ).exists()
        )

    def test_proposals_list_view(self):
        """Проверяет отображение списка предложений обмена."""
        ads_models.ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment_sender='Test'
        )
        response = self.client.get(reverse('ads:proposals_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ad1')

    def test_proposal_update_view(self):
        """Проверяет обновление предложения обмена через view."""
        proposal = ads_models.ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment_sender='Test'
        )
        response = self.client.post(
            reverse('ads:prop_update', args=[proposal.pk]),
            {
                'comment_sender': 'Updated comment',
                'status': ads_models.ExchangeProposal.DECLINED
            }
        )
        self.assertEqual(response.status_code, 302)
        proposal.refresh_from_db()
        self.assertEqual(proposal.comment_sender, 'Updated comment')
        self.assertEqual(proposal.status, ads_models.ExchangeProposal.DECLINED)
