from app import app
from app import sql_select, sql_insert, sql_delete, sql_update
from flask import request
from flask import jsonify


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    # On exécute un SELECT pour récupérer tous les players, dans une liste
    data = sql_select('''SELECT players_id, players_pseudo FROM players''')
    print(data)
    all_users = []
    # On parcourt la liste de joueurs renvoyée par la base
    for player_row in data:
        # On récupère les informations du player contenues dans le JSON, pour les stocker dans des variables
        players_id = str(player_row["players_id"])
        players_pseudo = player_row["players_pseudo"]


        # On récupère tous les chats qui sont dans une salle qui appartient au joueur qu'on parcourt
        sql_request = f'''SELECT * 
            FROM cats 
            JOIN rooms 
            ON cats.rooms_id = rooms.rooms_id 
            AND rooms.players_id = {players_id}'''

        cats = sql_select(sql_request)
        print(cats)

        # Le nombre de chats est égal à la taille de la liste
        cats_count = len(cats)

        # On crée un dictionnaire avec les informations attendues par le client
        user_dict = {'pseudo': players_pseudo,
                     'cats_count': cats_count,
                     'id': players_id}
        # On l'ajoute à la liste
        all_users.append(user_dict)

    # On retourne notre liste de dictionnaires convertie en JSON
    return jsonify(all_users)


@app.route('/login', methods=['POST'])
def login():
    # on récupère le json envoyé par le client
    formulaire_login = (request.get_json())

    # on récupère l'email
    email = formulaire_login["email"]

    # on check si l'email existe, si oui c'est good
    sql_request = f'''SELECT * FROM players WHERE players_email = "{email}"'''

    players_avec_cette_email = sql_select(sql_request)

    if len(players_avec_cette_email) > 0:

        # on récupère le password
        password = formulaire_login["password"]

        sql_request = f'''SELECT players_id FROM players WHERE players_email  = "{email}" AND players_password = "{password}"'''
        players_id_avec_cette_email_et_ce_password = sql_select(sql_request)

        if len(players_id_avec_cette_email_et_ce_password) > 0:
            print ("bon compte")
            player_id = {"id" : int(players_avec_cette_email[0]["players_id"])}
            return jsonify(player_id)

        else:
            return "mauvais mdp"

    else:
        return "mauvais email"

    #players_avec_ce_password = sql_select(sql_request)



    #return "Not implemented", 501


@app.route('/signup', methods=['POST'])
def sign_up():
    #on récupère le json envoyé par le client
    formulaire_inscription = (request.get_json())

    #on récupère l'email
    email = formulaire_inscription["email"]

    #on check si l'email existe, si oui on envoie une erreur
    sql_request = f'''SELECT * FROM players WHERE players_email = "{email}"'''

    players_avec_cette_email = sql_select(sql_request)

    if len(players_avec_cette_email) > 0:
        return "Email déjà existant", 503

    #on ajoute le joueur
    sql_request = f'''INSERT INTO players(players_pseudo, players_email, players_password)
    VALUES("{formulaire_inscription["pseudo"]}", 
    "{formulaire_inscription["email"]}", 
    "{formulaire_inscription["password"]}")'''

    players_id = sql_insert(sql_request)

    add_room(players_id, 0, 0, formulaire_inscription["seed"])

    return "OK", 200


@app.route('/users/<int:players_id>/rooms', methods=['GET', 'POST'])
def rooms_handling(players_id):
    if request.method == 'GET':
        return get_rooms_request(players_id)
    elif request.method == 'POST':
        return add_room_request(players_id, request.get_json())


def get_rooms_request(players_id):
    sql_request = f'''SELECT * FROM rooms WHERE players_id = "{players_id}"'''
    player_avec_la_room = sql_select(sql_request)
    #return(jsonify(player_avec_la_room), 200)

    for room in player_avec_la_room:
        sql_request = f'''SELECT * FROM cats WHERE rooms_id = "{room["rooms_id"]}"'''
        room["cats"] = sql_select(sql_request)

    print(player_avec_la_room)
    return jsonify(player_avec_la_room)



def add_room_request(players_id, request_json):
    print(request_json)
    return add_room(players_id, request_json["position_x"], request_json["position_y"], request_json["seed"])


def add_room(players_id, pos_x, pos_y, seed):
    sql_request = f'''SELECT * FROM rooms 
    WHERE players_id = "{players_id}"
    AND rooms_position_x = "{pos_x}"
    AND rooms_position_x = "{pos_y}"'''
    player_rooms_info = sql_select(sql_request)

    if len(player_rooms_info) > 0:
        return "Il y a déjà une room ici", 403
    else:
        sql_request = f'''INSERT INTO rooms (rooms_position_x, rooms_position_y, rooms_seed, players_id)
        VALUES("{pos_x}", "{pos_y}", "{seed}", "{players_id}")'''
        execute = sql_insert(sql_request)
        return {"id":execute}, 200


@app.route('/users/<int:players_id>/rooms/<int:rooms_id>', methods=['DELETE'])
def delete_room(players_id, rooms_id):
    sql_request = f'''SELECT * FROM cats WHERE rooms_id = "{rooms_id}"'''
    get_cats = sql_select(sql_request)

    if len(get_cats) > 0:
        return "Tu en peux pas supprimer car il y a des pauvres petits minouches dans cette room", 403
    else:
        sql_request = f'''DELETE FROM rooms WHERE players_id = "{players_id}" AND rooms_id = "{rooms_id}"'''
        sql_delete(sql_request)
        return "Ok la room est supprimée du coup !"


@app.route('/cats', methods=['GET'])
def get_free_cats():
    sql_request = f'''SELECT * FROM cats WHERE rooms_id IS NULL'''
    cats_adoptables = sql_select(sql_request)
    return jsonify(cats_adoptables), 200


@app.route('/cats/<int:cats_id>', methods=['PATCH', 'DELETE'])
def update_cat(cats_id):
    return "Not implemented", 501

