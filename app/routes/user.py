from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import desc

from app.models import db, Card, Set, User, Sale, Trade, Log, CardOwnership

from random import sample

from app.pack import get_pack

from app.forms import SearchForm

user = Blueprint('user', __name__)


def get_card_str(id_str):
    return Card.query.filter_by(id_str=id_str).first()

def get_card_id(id):
    return Card.query.filter_by(id=id).first()

def get_set(set):
    return Card.query.filter_by(set_name=set)


def element_of(val, iterable):
    for item in iterable:
        if item.id == val:
            return True
    else:
        return False


def get_lowest_sale(card_id):
    return Sale.query.filter_by(card_id=card_id,
                                status=0).filter(Sale.user_id != current_user.id).order_by(Sale.cost).first()


# list of locations a user can be in
# ('location', 'currency short', 'symbol')
locations = [('United States', 'USD', '$'), ('Russia', 'RUB', '₽'),
             ('EU', 'EUR', '€'), ('Japan', 'JPY', '¥'), ('Korea', 'KRW', '₩')]


@user.route('/profile')
@login_required
def profile():
    return redirect(url_for('user.mycards'))


@user.route('/profile/mycards', methods = ['GET','POST'])
@login_required
def mycards():
    '''Loop through user's cards and build a list of groups of 5 cards to make displaying easier.'''
    c = current_user.cards
    if len(c) > 0:
        a = [c[i * 5:(i + 1) * 5] for i in range((len(c) + 5 - 1) // 5)]
        while len(a[-1]) < 5:
            a[-1].append(0)
    else:
        a = []
        flash(
            'You currently do not own any cards. Buy cards or packs from the Marketplace!',
            'info')
    return render_template('mycards.html',
                            page=0,
                            title="My Cards",
                            cards=a)


@user.route('/profile/mysales')
@login_required
def mysales():
    '''Loop through user's sales and build a list of groups of 5 cards to make displaying easier.'''
    c = Sale.query.filter_by(user_id=current_user.id, status = 0).all()
    if len(c) > 0:
        a = [c[i * 5:(i + 1) * 5] for i in range((len(c) + 5 - 1) // 5)]
        while len(a[-1]) < 5:
            a[-1].append(0)
        x = 0
        y = 0
        while x < 5:
            while y < 5:
                if (a[x][y] != 0):
                    a[x][y] = Card.query.filter_by(id=a[x][y].card_id).first()
                y += 1
            x += 1
    else:
        a = []
        flash(
            'None of your cards are up for sale. Sell cards in the Marketplace!',
            'info')

    return render_template('mycards.html',
                            page=1,
                            title="My Sales",
                            cards=a)


@user.route('/profile/purchaseHist')
@login_required
def purchaseHist():
    '''Loop through a query of cards the user have bought and build a list of groups of 5 cards to make displaying easier.'''
    c = Sale.query.filter_by(status=1, buyer_id = current_user.id).all()
    print(c)
    s = []
    for sale in c:
        if sale.buyer_id == current_user.id and sale.user_id != current_user.id:
            s.append(sale)
    print(s)
    if len(s) > 0:
        a = [c[i * 5:(i + 1) * 5] for i in range((len(c) + 5 - 1) // 5)]
        while len(a[-1]) < 5:
            a[-1].append(0)
        x = 0
        y = 0
        while x < 5:
            while y < 5:
                if (a[x][y] != 0):
                    a[x][y] = Card.query.filter_by(id=a[x][y].card_id).first()
                y += 1
            x += 1
    else:
        a = []
        flash('You have not bought any cards. Buy cards in the Marketplace!',
              'info')

    return render_template('mycards.html',
                           page=3,
                           title="Purchase History",
                           cards=a)

@user.route('/profile/saleHist')
@login_required
def saleHist():
    '''Loop through a query of cards the user have sold and build a list of groups of 5 cards to make displaying easier.'''
    c = Sale.query.filter_by(status=1, buyer_id = current_user.id).all()
    c = Sale.query.filter_by(status=1, user_id = current_user.id).all()
    if len(c) > 0:
        a = [c[i * 5:(i + 1) * 5] for i in range((len(c) + 5 - 1) // 5)]
        while len(a[-1]) < 5:
            a[-1].append(0)
        x = 0
        y = 0
        while x < 5:
            while y < 5:
                if (a[x][y] != 0):
                    a[x][y] = Card.query.filter_by(id=a[x][y].card_id).first()
                y += 1
            x += 1
    else:
        a = []
        flash('You have not sold any cards. Sell cards in the Marketplace!',
              'info')

    return render_template('mycards.html',
                           page=3,
                           title="Sale History",
                           cards=a)

@user.route('/profile/tradeHist')
@login_required
def tradeHist():
    '''Loop through a query of trades the user have participated in and build a list of groups of 2 cards to make displaying easier.'''
    c = Trade.query.filter_by(status=1, acceptor_id = current_user.id).all()
    print(c)
    if len(c) == 0:
        flash('You have not traded any cards. Trade cards in the Marketplace!',
              'info')
    else:
        c = [c[i * 2:(i + 1) * 2] for i in range((len(c) + 2 - 1) // 2)]
        while len(c[-1]) < 2:
            c[-1].append(0)

    return render_template('mytrades.html',
                           page=3,
                           title="Trade History",
                           list=c)

@user.route('/profile/mytrades')
@login_required
def mytrades():
    '''Loop through user's trades and build a list of groups of 2 cards to make displaying easier.'''
    c = Trade.query.filter_by(user_id=current_user.id,status=0).all()
    print(c)
    if len(c) == 0:
        flash(
            'You do not have any cards up for trade. Trade cards in the Marketplace!',
            'info')
    else:
        c = [c[i * 2:(i + 1) * 2] for i in range((len(c) + 2 - 1) // 2)]
        while len(c[-1]) < 2:
            c[-1].append(0)

    return render_template('mytrades.html',
                            page=2,
                            title="My Trades",
                            list=c)


@user.route('/marketplace/cards', methods=['GET'])
@login_required
def cards():
    '''Display cards up for sale in the marketplace.'''
    #set certain cards as featured
    f = [
        'xy6-61', 'xy8-63', 'xy8-64', 'xy2-69', 'xy2-13', 'sm5-161', 'sm5-163',
        'sm6-140', 'sm11-247', 'smp-SM210'
    ]
    f = [get_card_str(n) for n in f]
    featured = [f[:5], f[5:]]

    #get the cards of a set that we manually call the newest one
    newest_set = 'Cosmic Eclipse'
    n = [c for c in get_set(newest_set)]
    n = sample(n, 10)
    new = [n[:5], n[5:]]

    #order the cards by how many times they've been sold and grab the 10 most popular
    p = Card.query.order_by(Card.num_sales)[:10]
    popular = [p[:5], p[5:]]

    return render_template('cards.html',
                           featured=featured,
                           new=new,
                           popular=popular)


@user.route('/marketplace/cards', methods=['POST'])
@login_required
def buyCards():
    '''Goes through all the necessary interactions that must happen when a card is bought.'''
    card = Card.query.filter_by(id=request.form['card']).first()
    anysale = Sale.query.filter_by(card_id=card.id,status=0).first()
    lowestsale = Sale.query.filter_by(card_id=card.id,status=0).filter(Sale.user_id != current_user.id).order_by(
        Sale.cost).first()
    if anysale == None:
        flash('This card is no longer on sale', 'danger')
        return redirect(url_for('user.cards'))
    elif lowestsale == None:
        flash('You cannot buy your own card', 'danger')
        return redirect(url_for('user.cards'))

    owner = User.query.filter_by(id=lowestsale.user_id).first()
    if (float(lowestsale.cost) <= float(current_user.balance)): #if the user has enough money to buy it
        current_user.balance -= lowestsale.cost
        owner.balance += lowestsale.cost
        current_user.cards.append(card)
        if lowestsale.user_id != 4:
            lowestsale.buyer = current_user
            owner.cards.remove(card)
            lowestsale.status = 1
            print(card not in owner.cards)
            if(card not in owner.cards):
                trades = Trade.query.filter_by(status=0,
                                               user_id=lowestsale.user_id,
                                               given_card_id=card.id).all()
                print(trades)
                if trades != None:
                    for trade in trades:
                        db.session.delete(trade)
        else:
            sale = Sale(lowestsale.card_id, lowestsale.cost, 1, 4, current_user.id)
            db.session.add(sale)
            db.session.commit()
        flash('You have bought ' + get_card_id(int(request.form['card'])).name, 'success')
    else:
        flash('You do not enough money to buy ' + request.form['card'],
              'danger')
    db.session.commit()
    return redirect(url_for('user.cards'))


@user.route('/marketplace/packs', methods=['GET'])
@login_required
def packs():
    '''Display packs up for sale in the marketplace.'''
    f = [
        'Legendary Collection', 'Legends Awakened', 'Legend Maker',
        'Legendary Treasures', 'Shining Legends'
    ]
    featured = [Set.query.filter_by(name=c).first() for c in f]

    n = [
        'Cosmic Eclipse', 'Hidden Fates', 'Unified Minds', 'Unbroken Bonds',
        'Detective Pikachu'
    ]
    new = [Set.query.filter_by(name=c).first() for c in n]

    p = [
        'Base', 'Ruby & Sapphire', 'Diamond & Pearl', 'Team Rocket',
        'Sun & Moon'
    ]
    popular = [Set.query.filter_by(name=c).first() for c in p]

    return render_template('packs.html',
                           featured=featured,
                           new=new,
                           popular=popular)


@user.route('/marketplace/packs', methods=['POST'])
@login_required
def buyPacks():
    '''Goes through all the necessary interactions that must happen when a pack is bought.'''
    cards = get_pack(request.form['set'])
    if (float(current_user.balance) >= 10):
        current_user.balance -= 10
        for card in cards:
            current_user.cards.append(card)
        flash('You have brought ' + request.form['set'], 'success')
    else:
        flash('You do not enough money to buy ' + request.form['set'],
              'danger')
    db.session.commit()
    cards = [cards[:5], cards[5:]]
    print(cards)
    return render_template('cardsinpack.html',
                            title="You Got:",
                            cards=cards)


@user.route('/marketplace/trades', methods=['GET', 'POST'])
@login_required
def trades():
    '''Goes through all the necessary interactions that must happen when a trade is accepted.'''
    if 'trade' in request.form.keys():
        requested_card = Card.query.filter_by(
            id=request.form['requested_card']).first()
        given_card = Card.query.filter_by(
            id=request.form['given_card']).first()
        other_user = User.query.filter_by(id=request.form['user']).first()
        if other_user.id == current_user.id:
            flash('You can\'t trade with yourself!', 'danger')
        elif element_of(int(requested_card.id), current_user.cards):
            flash('Trade completed!', 'success')

            current_user.cards.remove(requested_card)
            current_user.cards.append(given_card)
            other_user.cards.remove(given_card)
            other_user.cards.append(requested_card)
            trade = Trade.query.filter_by(id=request.form['trade']).first()
            trade.status += 1
            trade.acceptor_id = current_user.id
            if (requested_card not in current_user.cards): #checks for other trades
                trades = Trade.query.filter_by(user_id=current_user.id,
                                               request_card_id = requested_card.id,
                                               status = 0).all()
                if trades != None:
                    for trade in trades:
                        db.session.delete(trade)
                sales = Sale.query.filter_by(status=0,
                                             user_id=current_user.id,
                                             card_id=requested_card.id).all()
                if sales != None:
                    for sale in trades:
                        db.session.delete(sale)

            if (given_card not in other_user.cards):
                trades = Trade.query.filter_by(user_id=other_user.id,
                                               given_card_id = given_card.id,
                                               status = 0).all()
                if trades != None:
                    for trade in trades:
                        db.session.delete(trade)
                sales = Sale.query.filter_by(status=0,
                                             user_id=other_user.id,
                                             card_id=given_card.id).all()
                if sales != None:
                    for sale in trades:
                        db.session.delete(sale)
            db.session.commit()
        else:
            flash('You don\'t have that card!', 'danger')
    new = Trade.query.filter_by(status=0).order_by(Trade.id.desc())
    new1 = [new[:2], new[2:4], new[4:6]]
    new2 = [new[6:8], new[8:10], new[10:12]]
    return render_template('trades.html',
                            new_first=new1,
                            new_second=new2)


@user.route('/trade', methods=['GET', 'POST'])
@login_required
def trade():
    '''Goes through all the necessary interactions that must happen when a trade request is made.'''
    if len(current_user.cards) == 0:
        flash('You do not have any cards to trade!', 'danger')
        return redirect(url_for('user.trades'))
    if 'first_card' in request.form.keys(
    ) and 'second_card' in request.form.keys():
        flash('Your trade has been posted!', 'success')
        from app import app
        with app.app_context():
            t = Trade(request.form['second_card'], request.form['first_card'],
                      current_user.id)
            db.session.add(t)
            db.session.commit()
            return redirect(url_for('user.trades'))
    return render_template('trade.html',
                            query=Card.query)


@user.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    '''Goes through all the necessary interactions that must happen when a sale request is made.'''
    if len(current_user.cards) == 0:
        flash('You do not have any cards to sell!', 'danger')
        return redirect(url_for('user.cards'))
    if 'card' in request.form.keys() and 'price' in request.form.keys():
        num = 0
        for card in current_user.cards:
            if int(card.id) == int(request.form['card']):
                num += 1

        if (len(Sale.query.filter_by(user_id=current_user.id,card_id=request.form['card']).all()) >= num):
            flash( 'All of your copies of ' +
                str(
                    Card.query.filter_by(id=request.form['card']).first().name)
                + ' are already on sale!', 'danger')
            return render_template('sales.html')

        flash('Your sale has been posted!', 'success')
        from app import app
        with app.app_context():
            Card.query.filter_by(
                id=request.form['card']).first().num_sales += 1
            sale = Sale(request.form['card'], request.form['price'], 0,
                        current_user.id, None)
            db.session.add(sale)
            db.session.commit()
        return redirect(url_for('user.mysales'))
    return render_template('sales.html')


@user.route('/search', methods=['GET', 'POST'])
@login_required
def search():

    SEARCH_LIMIT = 100
    PER_ROW = 3

    form = SearchForm()

    full_results = None

    if form.validate_on_submit():
        results = Card.query.filter(
            Card.name.like('%{}%'.format(form.search.data))).all()

        sales = Sale.query.all()
        all_ids = set([i.card_id for i in sales])

        results = [i for i in results if i.id in all_ids]

        type_filter = form.types.data
        rarity_filter = form.rarities.data

        if len(type_filter) != 0:
            results = [
                i for i in filter(lambda x: x.type in type_filter, results)
            ]
        if len(rarity_filter) != 0:
            results = [
                i for i in filter(lambda x: x.rarity in rarity_filter, results)
            ]

        # cut results off
        results = results[:SEARCH_LIMIT]

        # pad results
        while len(results) % PER_ROW != 0:
            results.append(None)

        full_results = []

        print(full_results)

        for i in range(len(results) // PER_ROW):
            full_results.append(results[i * PER_ROW:(i + 1) * PER_ROW])
    else:
        form.rarities.data = []
        form.types.data = []

    return render_template('search.html',
                           form=form,
                           query=form.search.data,
                           limit=SEARCH_LIMIT,
                           results=full_results,
                           rarities=','.join(form.rarities.data),
                           types=','.join(form.types.data))


@user.route('/viewcard/<id>')
@login_required
def view_card(id):
    sales = Sale.query.filter_by(card_id=id,status=0).order_by(Sale.cost).all()
    print(sales)
    request_trades = Trade.query.filter_by(request_card_id=id).all()
    given_trades = Trade.query.filter_by(given_card_id=id).all()
    card = Card.query.get(id)

    return render_template('viewcard.html',
                           card=card,
                           lowestseller=sales[0],
                           sales=sales[1:],
                           gtrades=given_trades,
                           rtrades=request_trades)
