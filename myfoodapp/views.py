import requests
import json
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic, View
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Categories, Food, foodcate, saved
from .forms import ConnexionForm, NewUserForm

# Create your views here.


class IndexView(View):
    template_name = 'myfoodapp/index.html'

    def get(self, request):
        return render(request, self.template_name)


def creation(request):
    errorusr = False
    erroremail = False

    created = False
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            email = form.cleaned_data["email"]
            if User.objects.filter(username=username).exists():
                errorusr = True
            if User.objects.filter(email=email).exists():
                erroremail = True
            else:
                newuser = User.objects.create_user(
                    username, email, password, first_name=first_name, last_name=last_name)
                created = True
                if not newuser:  # Si l'objet renvoyé n'est pas None
                    error = True
    else:
        form = NewUserForm()

    return render(request, 'myfoodapp/creation.html', locals(), {'created' : created})


def connexion(request):
    error = False
    if request.method == "POST":
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            # Nous vérifions si les données sont correctes
            user = authenticate(username=username, password=password)
            if user:  # Si l'objet renvoyé n'est pas None
                login(request, user)  # nous connectons l'utilisateur
            else:  # sinon une erreur sera affichée
                error = True
    else:
        form = ConnexionForm()

    return render(request, 'myfoodapp/connexion.html', locals())


def deconnexion(request):
    logout(request)
    return redirect(reverse('myfoodapp:connexion'))

def legals(request):
    return render(request, 'myfoodapp/legals.html')

class CompteView(generic.ListView):
    model = User
    template_name = 'myfoodapp/compte.html'

def display(request):
    template_name = 'myfoodapp/populate.html'
    return render(request, template_name)

class PopulateView(generic.ListView):
    model = User
    template_name = 'myfoodapp/populate.html'

    def get(self, request):
        display(request)
        categories_list = ["Boissons", "Viandes", "Surgelés", "Conserves",
                           "Fromages", "Biscuits", "Chocolats", "Apéritifs", "Soupes", "Pizzas",
                           "Snacks", "Epicerie", "Sauces", "Gâteaux", "Yaourts", "Jus de fruits",
                           "Pains", "Vins", "Huiles", "Miels"]
        for category in categories_list:
            print(category)
            print(Categories.objects.filter(name_categories=category).exists())
            if not Categories.objects.filter(name_categories=category).exists():
                my_insert = Categories(name_categories=category)
                my_insert.save()
                page = 1
                k = 0
                while k < 40:
                    i = 0
                    while i < 19 and k < 40:
                        url = "https://fr.openfoodfacts.org/category/" + category + "/\
            " + str(page) + ".json"
                        response = requests.get(url)
                        if(response.ok):
                            jData = json.loads(response.content)
                            print(jData.get('products')[i].get(
                                'nutrition_grades_tags')[0])
                            print(i)
                            if len(jData.get('products')[i].get('nutrition_grades_tags')[0])\
                                    is not 1:
                                i = i + 1
                            elif jData.get('products')[i].get('product_name_fr') is None:
                                i = i + 1
                            elif len(jData.get('products')[i].get('product_name_fr')) < 1:
                                i = i + 1
                            else:
                                product_name = str(jData.get('products')[
                                                   i].get('product_name_fr'))
                                product_name = product_name.replace('\\', '')
                                quantity = str(jData.get('products')[
                                               i].get('quantity'))
                                quantity = quantity.replace('\\', '')
                                dangers = str(jData.get('products')[
                                              i].get('traces'))
                                dangers = dangers.replace('\\', '')
                                stores = str(jData.get('products')
                                             [i].get('stores'))
                                stores = stores.replace('\\', '')
                                nutri_score = str(jData.get('products')[
                                                  i].get('nutrition_grades_tags')[0])
                                nutri_score = nutri_score.replace('\\', '')
                                link = str(jData.get('products')[i].get('url'))
                                img = str(jData.get('products')
                                          [i].get('image_url'))
                                if not Food.objects.filter(name_food=product_name).exists():
                                    my_insert = Food(
                                        name_food=product_name,
                                        quantity_food=quantity,
                                        dangers_food=dangers,
                                        store_food=stores,
                                        nutri_score_food=nutri_score,
                                        link_food=link,
                                        img_food=img,
                                    )
                                    my_insert.save()
                                    my_id = my_insert.id

                                    id_category = Categories.objects.only(
                                        'id').get(name_categories=category).id

                                    if not foodcate.objects.filter(Food_id=my_id, Categories_id=id_category).exists():
                                        print("food id: "+str(my_id) +
                                              " cate : "+str(id_category))
                                        my_insert = foodcate(Food_id=Food.objects.get(
                                            id=my_id), Categories_id=Categories.objects.get(id=id_category))
                                        my_insert.save()

                                k = k + 1
                                i = i + 1
                    page = page + 1
                    print(k)

        return render(request, self.template_name)


def searching_cat(product):
    id_prod = Food.objects.only('id').get(name_food=product).id
    id_cat = foodcate.objects.only('Categories_id_id').get(
        Food_id_id=id_prod).Categories_id_id
    name_cat = Categories.objects.only(
        'name_categories').get(id=id_cat).name_categories
    print(name_cat)
    return name_cat


def get_better_food(product, category):
    nutri_score = Food.objects.only('nutri_score_food').get(
        name_food=product).nutri_score_food
    nutri_score = ord(nutri_score)

    id_category = Categories.objects.only(
        'id').get(name_categories=category).id
    candidate_ids = foodcate.objects.filter(
        Q(Categories_id_id=id_category)).values('Food_id_id')

    results = []

    for id in candidate_ids:
        candidate_score = Food.objects.only('nutri_score_food').get(
            id=id['Food_id_id']).nutri_score_food
        candidate_score = ord(candidate_score)
        print(candidate_score)
        if candidate_score < nutri_score:
            results.append(id)

    print(results)

    return results


class SearchView(generic.ListView):
    template_name = 'myfoodapp/search.html'

    def get(self, request):
        aliment = request.GET['product']
        id_to_sub = Food.objects.only('id').get(name_food=aliment).id
        bkg_img = Food.objects.only('img_food').get(id=id_to_sub).img_food
        category = searching_cat(aliment)
        list_id = get_better_food(aliment, category)
        temp = []
        my_result = []
        for id in list_id:
            temp = Food.objects.filter(id=id['Food_id_id']).values(
                'name_food', 'nutri_score_food', 'id', 'img_food')
            my_result.append(
                {'name_food': temp[0]['name_food'], 'nutri_score_food': temp[0]['nutri_score_food'],
                 'id': temp[0]['id'], 'img_food' : temp[0]['img_food']})

        return render(request, self.template_name, {'aliment': aliment, 'category': category,
                                                     'my_result': my_result, 'id_to_sub': id_to_sub,
                                                     'bkg_img' : bkg_img})


class ProductView(generic.ListView):
    template_name = 'myfoodapp/product.html'

    def get(self, request):
        product_id = request.GET['product']

        temp = Food.objects.filter(id=product_id).values(
            'name_food', 'nutri_score_food', 'quantity_food', 'link_food', 'img_food')
        my_product = ({'name_food': temp[0]['name_food'], 'nutri_score_food': temp[0]['nutri_score_food'],
                       'quantity_food': temp[0]['quantity_food'], 'link_food': temp[0]['link_food'],
                       'img_food' : temp[0]['img_food']})

        score_range = ['a', 'b', 'c', 'd', 'e']

        return render(request, self.template_name, {'my_product': my_product, 'score_range': score_range})


class SavedView(generic.ListView):
    # Id might lead to confusion
    # issub = is substituted
    # sub = substitute the food. It is the new food
    template_name = 'myfoodapp/saved.html'

    def get(self, request):
        sub = request.GET['sub']
        tosub = request.GET['tosub']
        id_user = request.user
        id_user = id_user.id
        inserted = False
        logged = False
        if id_user is not None:
            logged = True
            if not saved.objects.filter(User_id_saved_id=id_user, Food_id_foodissub_id=tosub, Food_id_foodsub_id=sub).exists():
                my_insert = saved(
                    User_id_saved_id=id_user, Food_id_foodissub_id=tosub, Food_id_foodsub_id=sub)
                my_insert.save()
                inserted = True

        return render(request, self.template_name, {'inserted': inserted, 'logged': logged})

class MyFoodView(generic.ListView):
    template_name = 'myfoodapp/viewsaved.html'

    def get(self, request):
        my_result = []
        #if request.user.is_authenticated():
        #    id_user = user.id
        id_user = request.user
        id_user = id_user.id
        if saved.objects.filter(User_id_saved_id=id_user).exists():
            temp = saved.objects.filter(User_id_saved_id=id_user).values(
            'Food_id_foodissub_id', 'Food_id_foodsub_id')
            for i in temp:
                temp_sub = Food.objects.filter(id=i['Food_id_foodsub_id']).values(
                    'name_food', 'nutri_score_food', 'img_food', 'id')
                my_result.append(
                    {'name_food': temp_sub[0]['name_food'], 'nutri_score_food': temp_sub[0]['nutri_score_food'],
                    'id': temp_sub[0]['id'], 'img_food' : temp_sub[0]['img_food'],
                    'food_is_sub_id' : i['Food_id_foodissub_id']})

        return render(request, self.template_name, {'my_result': my_result})   

class DetailsView(generic.ListView):
    template_name = 'myfoodapp/details.html'

    def get(self, request):
        sub = request.GET['sub']
        issub = request.GET['issub']
        sub_det = Food.objects.filter(id=sub).values(
                'name_food', 'img_food', 'nutri_score_food')
        issub_det = Food.objects.filter(id=issub).values(
                'name_food', 'img_food', 'nutri_score_food')
        return render(request, self.template_name, {'sub_id': sub, 'issub_id': issub,
                                                    'sub_name': sub_det[0]['name_food'],
                                                    'sub_img': sub_det[0]['img_food'], 
                                                    'sub_score': sub_det[0]['nutri_score_food'], 
                                                    'issub_name': issub_det[0]['name_food'],
                                                    'issub_img': issub_det[0]['img_food'],
                                                    'issub_score': issub_det[0]['nutri_score_food']})