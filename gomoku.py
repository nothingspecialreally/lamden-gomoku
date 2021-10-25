import currency as token  # may not work

game_state = Hash()
owner = Variable()

@construct
def init():
    game_state['last_id'] = 0
    owner.set(ctx.caller)


@export
def create_game(size: int = 15, maximum_turn_time: int = 10, wager: float = False):
    assert type(size) is int and type(maximum_turn_time) is int, 'Size and turn time must be integer!'
    # we can also force them to be below 0, but size should have implicit error and max_turn_time would function as expected

    size -= 1  # off by one error

    game_id = game_state['last_id']
    game_state['last_id'] += 1
    game_state[game_id, 'size'] = size
    game_state[game_id, 'open'] = True
    game_state[game_id, 'completed'] = False
    game_state[game_id, 'wager'] = wager
    game_state[game_id, 'players'] = [ctx.caller]
    game_state[game_id, 'last_turn'] = 1
    game_state[game_id, 'maximum_turn_time'] = maximum_turn_time

    temp_list = ['' for number in range(size)]
    game_state[game_id] = [temp_list for number in range(size)]

    if wager:
        token.transfer_from(to=ctx.this, amount=wager, main_account=ctx.caller)

    return game_id


@export
def join_game(game_id: int):
    assert game_state[game_id, 'open'] is True, 'Game not created or already filled!'
    assert ctx.caller not in game_state[game_id, 'players'], 'Cannot join own game!'

    if game_state[game_id, 'wager']:
        token.transfer_from(to=ctx.this, amount=game_state[game_id, 'wager'], main_account=ctx.caller)

    game_state[game_id, 'players'].append(ctx.caller)
    game_state[game_id, 'wager'] = wager
    game_state[game_id, 'open'] = False

    return True


@export
def play(column: int, row: int, player_id: int, game_id: int):  # janky as shit, should use lookup (but I'm lazy)
    assert ctx.caller == game_state[game_id, 'players'][player_id], 'Not correct player or not in game!'
    assert game_state[game_id, 'completed'] is False, 'Game already concluded!'
    assert game_state[game_id][column][row] is None, 'Position already occupied!'
    assert column <= game_state[game_id, 'size'] and row <= game_state[game_id, 'size'], 'Coordinates out of bounds!'
    assert game_state[game_id, 'last_turn'] != player_id, 'Not your turn!'

    game_state[game_id][column][row] = player_id
    game_state[game_id, 'last_turn'] = player_id
    game_state[game_id, 'last_turn_time'] = now

    diagnoal_desc = []
    diagnoal_asc = []
    vertical = []
    horizontal = []
    for number in range(-4, 4):
        diagnoal_desc.append([column - number, row + number])
        diagnoal_asc.append([column - number, row - number])
        vertical.append([column, row + number])
        horizontal.append([column + number, row])

    for x in [diagnoal_desc, diagnoal_asc, vertical, horizontal]:
        x = fit_to_range(game_state[game_id, 'size'], x)
        win = check_win(game_id, player_id, x)
        if win is True:
            break

    if win is True:
        game_state[game_id, 'completed'] = player_id
        if game_state[game_id, 'wager']:
            token.transfer(to=ctx.caller, amount=game_state[game_id, 'wager'] * 2)
        return True

    return None


@export
def call_game_default(player_id: int, game_id: int):
    assert game_state[game_id, 'last_turn'] == player_id, 'Cannot force default of self!'
    assert ctx.caller == game_state[game_id, 'players'][player_id], 'Cannot call, not player!'
    assert now - game_state[game_id, 'last_turn_time'] > datetime.timedelta(weeks=0, days=game_state[game_id, 'maximum_turn_time'], hours=0, minutes=0, seconds=0), 'Other player still has time!'  # probably don't need ll of these

    game_state[game_id, 'completed'] = player_id
    if game_state[game_id, 'wager']:
        token.transfer(to=ctx.caller, amount=game_state[game_id, 'wager'] * 2)

    return True


def fit_to_range(board_size: int, possible_positions: list):
    for position in list(possible_positions):
        for coordinate in position:
            if int(coordinate) > board_size or int(coordinate) < 0:
                possible_positions.remove(position)
                break

    return possible_position


def check_win(player_id: int, possible_positions: list, game_id=int):
    count = 0
    for position in list(possible_positions):
        if game_state[game_id][position[0]][position[1]] == player_id:
            count += 1
        else:
            count = 0
        if count >= 5:
            return True

    return False

@export
def change_owner(new_owner: str):
  assert owner.get() == ctx.caller, "Not the owner!"
  owner.set(new_owner)

@export
def sweep_coins(amount: float):
  assert owner.get() == ctx.caller or ctx.caller in owner.get(), "Not the owner!"
  token.transfer(to=ctx.caller, amount=amount)