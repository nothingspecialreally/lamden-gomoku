# dummy interface for testing purposes only

balances = Hash(default_value=0)


@construct
def seed():
    balances[ctx.caller] = 2147483647


@export
def transfer(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'

    sender = ctx.caller

    assert balances[sender] >= amount, 'Not enough coins to send!'

    balances[sender] -= amount
    balances[to] += amount


@export
def balance_of(account: str):
    return balances[account]


@export
def allowance(owner: str, spender: str):
    return balances[owner, spender]


@export
def approve(amount: float, to: str):
    assert amount > 0, 'Cannot send negative balances!'

    sender = ctx.caller
    balances[sender, to] += amount
    return balances[sender, to]


@export
def transfer_from(amount: float, to: str, main_account: str):
    assert amount > 0, 'Cannot send negative balances!'

    sender = ctx.caller

    assert balances[main_account] >= amount, 'Not enough coins to send!'
    assert balances[main_account, sender] >= amount, 'Not enough coins approved to send! You have {} and are trying to spend {}'\
        .format(balances[main_account, sender], amount)

    balances[main_account, sender] -= amount
    balances[main_account] -= amount

    balances[to] += amount


@export  # FOR MOCKing
def set_balance(amount: float):
    balances[ctx.caller] = amount
