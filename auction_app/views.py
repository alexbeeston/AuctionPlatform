import datetime
import random
import string

from django.shortcuts import render
from .models import *
from .forms import *
from django.utils import timezone
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from .debug_settings import *


@login_required
def home(request):
    if request.method == "POST":
        # for key in request.POST:
        #     print(f"\t{key} => {request.POST[key]}")
        request.POST = request.POST.copy() #create a mutable post
        request.POST['published'] = not getBool(request.POST['published'])
        auctionType = request.POST['type']
        auction = Auction.objects.filter(type=auctionType).first()
        form = AuctionForm(request.POST, instance=auction)
        form.save()
    silentAuction = Auction.objects.filter(type='silent').first()
    silentForm = AuctionForm(instance=silentAuction)
    liveAuction = Auction.objects.filter(type='live').first()
    liveForm = AuctionForm(instance=liveAuction)
    auctionForms = [silentForm, liveForm]
    context={"forms":auctionForms} #data to send to the html page goes here
    return render(request, 'home.html', context)

def getBool(str):
    if str.lower() == 'true':
        return True
    else:
        return False

@login_required
def init_test_db(request):
    if DEBUG:
        AuctionUser(
            username="user1",
            password="pass1212",
            email="email@email.com",
            first_name="tommy",
            last_name="thompson",
            auction_number=20,
        ).save()
        AuctionUser(
            username="user2",
            password="pass1212",
            email="email@email.com",
            first_name="johnny",
            last_name="johnson",
            auction_number=10,
        ).save()
        Rule(title="Rules & Announcements",
                last_modified=timezone.now(),
                rules_content="Insert rules here",
                announcements_content="Insert announcements here"
        ).save()
        silentAuction = Auction(type="silent")
        silentAuction.save()
        liveAuction = Auction(type="live")
        liveAuction.save()
        for i in range(10):
            item = SilentItem(
                title=randomString(), 
                description=randomString(), 
                imageName=randomString(), 
                auction=silentAuction
            )
            item.save()
            user = AuctionUser.objects.all().first()
            user.save()
            bid = Bid(amount=0, user=user, item=item).save()

            # populated the live database too
            itemLive = LiveItem(
                title=randomString(),
                description=randomString(),
                imageName=randomString(),
                auction=silentAuction,
                orderInQueue=i
            )
            itemLive.save()
        return redirect(login)
    else:
        return HttpResponseNotFound()

@login_required
def live(request):
    #this prevents non admins from getting to this page if its not a published auction
    liveAuction = Auction.objects.filter(type='live').first()
    if not liveAuction.published and not request.user.is_superuser:
        return redirect(home)
    # handle later
    # liveAuction = Auction.objects.filter(type='live').first()
    # if not liveAuction.published and not request.user.is_superuser:
    #     return redirect(home)


    # add bidder # stuff
    try:
        currentItem = LiveItem.objects.filter(sold=False).get(orderInQueue=1)
    except Exception as e:
        return HttpResponse("Error (there are probably more than one items in the database with an orderInQueue equal to 1. Here's the full error from django: " + str(e))

    context = {
        'currentItem': currentItem,
        'items': LiveItem.objects.all().filter(sold=False).exclude(orderInQueue=1)
    }
    return render(request, 'live.html', context)

def sellLiveItem(request):
    try:
        currentItem = LiveItem.objects.get(pk=request.POST['itemID']).sold= True
        currentItem.sold = True
        currentItem.save()
    except Exception as e:
        return HttpResponse('Error: the public key of the item that was bid on does not exit in the database. Django error: ' + str(e))

    winner = request.POST['number']
    amount = request.POST['amount']
    for liveItem in LiveItem.objects.all().filter(sold=False): # optimize by maintaining a pointer to the next item, or the index of the next item to be visited, rather than decrementing all items and querying for the fist item
        liveItem.orderInQueue -= 1
        liveItem.save()

    return HttpResponse(str(winner) + str(amount))

@login_required
def payment(request):
    users = AuctionUser.objects.all()
    context={"users": users}#data to send to the html page goes here
    return render(request, 'payment.html', context)

@login_required
def rules(request):
    #get a rules object from db or create a blank one
    rules = Rule.objects.all().first()
    empty = False
    if not rules:
        empty = True
        rules = Rule()

    if request.method == "POST":
        if empty:
            form = RulesForm(request.POST) #creates new rules object when saved
        else: 
            form = RulesForm(request.POST, instance=rules) #update the existing rules with post data
        form.save()
        return redirect(home)
    else:
        form = RulesForm(instance=rules) #populate form with db or blank data
        context = {
            "rules": rules,
            "form":form
        }
    return render(request, 'rules.html', context)

def randomString(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))
       
@login_required
def create_item(request):
    if request.method == "POST" and request.user.is_superuser:
        for key in request.POST:
            print(f"\t{key} => {request.POST[key]}")
        request.POST = request.POST.copy() #make the post mutable
        # #select the correct item type
        # print(request.POST.get("auction", False))
        # id = request.POST.get("auction", False)
        # auction = Auction.objects.get(pk=id)
        # print(auction)
        # request.POST['auction'] = auction
        request.POST['end'] = datetime.datetime.strptime(request.POST['end'], '%Y-%m-%dT%H:%M')
        item = SilentItemForm(request.POST)
            # auction = Auction.objects.filter(type=Auction.SILENT).first()
            # request.POST['auction'] = auction
        # elif request.POST.get("auction", False) == Auction.LIVE:
        #     # auction = Auction.objects.filter(type=Auction.LIVE).first()
        #     # request.POST['auction'] = auction
        #     item = LiveItemForm(request.POST)

        if item.is_valid():
            item.save()
        else:
            print("invalid form request")
            print(item.errors)

        if request.POST.get("type", False) == 'silent':
            return redirect(silent) 
        elif request.POST.get("type", False) == 'live':
            return redirect(live)
    else:
        return HttpResponseForbidden()

@login_required                    
def silent(request):
    #this prevents non admins from getting to this page if its not a published auction
    silentAuction = Auction.objects.filter(type='silent').first()
    if not silentAuction.published and not request.user.is_superuser:
        return redirect(home)

    createItemForm = SilentItemForm(initial={'auction':silentAuction})
    # createItemForm.fields['start'].widget = forms.DateTimeInput(attrs={'type':'datetime-local'})
    # createItemForm.fields['end'].widget = forms.DateTimeInput(attrs={'type':'datetime-local'})
    # createItemForm.fields['auction'].widget = forms.HiddenInput()
    context = {
        'objects': getCategories(request),
        'createItem': createItemForm,
    }

    return render(request, 'silent.html', context)

def getBidItemForm():
    mylist = []
    bidlist = []
    for item in SilentItem.objects.all():
        bidlist.append(getBiggestBidForItem(item))
    itemlist = list(SilentItem.objects.all())
    formlist = []
    for form in SilentItem.objects.all():
        formlist.append(BidForm(initial={'amount': getBiggestBidForItem(form).amount}))
    for i in range(len(SilentItem.objects.all())):
        mylist.append((bidlist[i], itemlist[i], formlist[i]))
    return mylist

def getBiggestBidForItem(item):
    bids = Bid.objects.filter(item=item)
    bigbid = Bid()
    tracker = 0.0
    for bid in bids:
        if bid.amount >= tracker:
            bigbid = bid
            tracker = bigbid.amount
    return bigbid

@login_required
def submit_bid(request):
    if request.method == 'POST':
        # for key in request.POST:
        #     print('#####', key, request.POST[key])
        amount = request.POST['amount']
        id = request.POST['item_id']
        bidform = BidForm(request.POST)
        if bidform.is_valid():
            item = SilentItem.objects.get(id=id)
            if float(amount) > getBiggestBidForItem(item).amount:
                new_bid = Bid(item=item, amount=amount, user=AuctionUser.objects.get(username=request.user.username))
                new_bid.save()
        else:
            # this means invalid data was posted
            print("invalid data")

    return HttpResponseRedirect("/silent")


def getCategories(request):
    biditemform = getBidItemForm()
    winning = []
    bidon = []
    unbid = []
    for bid, item, form in biditemform:
        if str(bid.user) == str(request.user.username) and bid.amount != 0.0:
            winning.append((bid, item, form))
        elif userHasBidOn(item, request):
            bidon.append((bid, item, form))
        else:
            unbid.append((bid, item, form))
    return (winning, 'Winning'), (bidon, 'Bid On'), (unbid, 'Not Bid On')


def userHasBidOn(item, request):
    bids = Bid.objects.filter(item=item)
    for bid in bids:
        if str(bid.user) == str(request.user.username) and bid.amount != 0.0:
            return True
    return False

@login_required
def users(request):
    users = AuctionUser.objects.all()
    form = CreateAccountForm()
    print(form.fields)
    form.fields['password1'].widget = forms.HiddenInput()
    form.initial['password1'] = "ax7!bwaZc"
    form.fields['password2'].widget = forms.HiddenInput()
    form.initial['password2'] = "ax7!bwaZc"
    if request.method == 'POST':
        form_data = request.POST.copy()
        form_data.update(password1="ax7!bwaZc")
        form_data.update(password2="ax7!bwaZc")
        form = CreateAccountForm(form_data)
        # print(form.is_valid())
        if form.is_valid():
            #save data
            form.save()
            users = AuctionUser.objects.all()
            form = CreateAccountForm()
            context = {
                "users": users,
                "form": form
            }
            return render(request, 'users.html', context)
        else:
            context = {
                "users": users,
                "form":form}
            # print(form.cleaned_data)
            # print(form.errors) #NEED TO PRINT SOME ERRORS TO THE USER SOMEHOW
            return render(request, 'users.html', context)
    else:
        #first visit
        context={"users": users,
                 "form": form}#data to send to the html page goes here
        return render(request, 'users.html', context)

@login_required
def afterLogin(request):
    #login the user
    login(request, request.user)
    if request.user.is_superuser:
        return redirect(home)
    else:
        return redirect(rules)

@login_required
def updateAuctionNumber(request):
    #do update
    for key in request.POST:
        print(f"\t{key} => {request.POST[key]}")
    username = request.POST['username']
    user = AuctionUser.objects.get(username=username)
    user.auction_number = request.POST['auction_number']
    user.save()
    return redirect(users)

#great example of form handling
def create_account(request):
    if request.method == 'POST':
        #create a form object from post data
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            #save data and login the resulting user
            print(form.cleaned_data)
            user = form.save()
            login(request, user)
            #redirect to rules view
            return redirect(rules)
        else:
            #form data will be sent back to page because it was invalid
            context = {"form":form}
    else:
        #generates a blank form 
        form = CreateAccountForm()
        context = {"form":form}
    #send back to create account template with the form to render
    return render(request, "CreateAccount.html", {"form":form})
