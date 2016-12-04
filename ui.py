from functools import partial
import logging

from nc import init_ui, printw, getstr, clear, alert
from menu import Menu, IdeaMenu
from idea import Idea

windows = init_ui()
print0 = partial(printw, windows[0])
print1 = partial(printw, windows[1])
print2 = partial(printw, windows[2])
print3 = partial(printw, windows[3])
read = partial(getstr, windows[3])


def list_ideas(count):
    ideas = []
    for i in range(count):
        idea = Idea()
        ideas.append(idea)

    return select_idea("Choose your idea", ideas)


def initproject(all_budget):
    idea = list_ideas(15)
    clear(windows[1])

    idea_pitch = " ".join(idea.pitch.split(" ")[1:])
    print1("So you have an idea, you are going to build {}".format(idea_pitch))
    print1("What's the name of the project?")

    name = str(read(), 'utf-8')

    budget = all_budget + 1

    clear(windows[1])

    while budget > all_budget:
        print1("You have $10000.")
        print1("Your daily personal expense is $25.")
        print1("How much budget do you want to allocate to your project?")
        budget = int(read())

    clear(windows[1])

    return name, budget, idea


def print_info(project, last, key, char="", reverse=False, multiplier=1):
    val = getattr(project, key)
    print0(char + str(int(val*multiplier)), end="")

    if reverse:
        positive = 1
        negative = 2
    else:
        positive = 2
        negative = 1

    if last:
        last_val = getattr(last, key)
        delta = int(val) - int(last_val)
        if delta < 0:
            print0("({})".format(delta), color=negative, end="")
        elif delta >0:
            print0("(+{})".format(delta), color=positive, end="")

    print0()


def print_project(project, used_resources, player, last_state):
    clear(windows[0])
    print0("Day {}".format(used_resources.turn_count))
    print0("Your Wallet: ${}\nYour shares: %{}".format(player.money, player.shares))

    print0("-------------------------")
    print0()

    print0(project.name.capitalize(), color=4)
    print0(project.pitch)

    print0("-------------------------")
    print0()

    print0("Budget", end=": ")
    print0("$" + str(project.money), color=2)

    print0("Cash Flow", end=": ")
    print0("$" + str(project.cash_flow), color=2)

    print0("Productivity", end=": ")
    print_info(project, last_state, 'productivity', multiplier=100)

    print0("Rema. Features", end=": ")
    print_info(project, last_state, 'features', reverse=True)

    print0("Bugs", end=": ")
    print_info(project, last_state, 'bugs', reverse=True)

    print0("Technical Debt", end=": ")
    print_info(project, last_state, 'technical_debt', reverse=True)

    print0("Documentation", end=": ")
    print_info(project, last_state, 'documentation')

    print0("Server Costs", end=": ")
    print_info(project, last_state, 'server_maintenance', char="$", reverse=True)

    print0("Design Need", end=": ")
    print_info(project, last_state, 'design_need', reverse=True)


def cli(objects, entities, used_resources, turn_events, last_state):
    player = objects[0]
    project = objects[1]

    logger = logging.getLogger('soyu')
    logger.debug(turn_events)
    for event in turn_events:
        a, b = alert(windows[4], str(event))
        del a
        del b
    project.turn_events = []

    clear(windows[1])

    print_project(project, used_resources, player, last_state)

    unlocked_entities = [entity for entity in entities if entity.unlocked and not entity.limit_reached()]
    limited_entities = [entity for entity in entities if entity.limit_reached()]

    print_limited(objects)
    action = select("What do you do?", unlocked_entities)

    if not action:
        return None
    return action


def print_limited(entities):
    clear(windows[2])
    print2("You have:")
    entities = {x.message: x for x in entities}.values()
    for entity in entities:
        print2("{}x {}".format(entity.current_amount, entity.message))


def select(question, choices):
    print1(question)
    answer_menu = Menu(choices, windows[1])
    answer = answer_menu.display()
    try:
        answer = int(answer)
    except (ValueError, TypeError):
        answer = False

    if not answer:
        return None
    else:
        if answer <= len(choices) - 1 :
            return choices[int(answer)]
        else:
            return None


def select_idea(question, choices):
    print1(question)
    answer_menu = IdeaMenu(choices, windows[1])
    answer = answer_menu.display()
    try:
        answer = int(answer)
    except (ValueError, TypeError):
        answer = 0

    return choices[int(answer)]


def win(project):
    clear(windows[1])
    print1("---------")
    print1("YOU WON")
    print1("---------")
    print1("Score: {}".format(project.score))
    windows[1].getch()


def over(project):
    clear(windows[1])
    print1("---------")
    print1("GAME OVER")
    print1("---------")
    print1("Score: {}".format(project.score))
    windows[1].getch()
