import discord
from discord.ext import commands
import datetime
import json
import random
import asyncio
from discord.file import File

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

TICKET_CATEGORY_NAME = "Tickets"
HELPER_ROLE_NAME = "Helper"
ticket_holders = set()
Token = ''

PERMISSION_ROLE_ID = 1163855249585483926

TICKETS_FILE = 'tickets.json'


def load_tickets():
    try:
        with open('tickets.json', 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    except FileNotFoundError:
        return {}


def save_tickets(tickets):
    with open('tickets.json', 'w') as file:
        json.dump(tickets, file, indent=4)


def save_user_to_json(user_id):
    data = load_data_from_json()
    data[user_id] = {}
    with open('users.json', 'w') as file:
        json.dump(data, file, indent=4)


def load_data_from_json():
    data = {}

    try:
        with open('users.json', 'r') as file:
            file_content = file.read().strip()
            if file_content:
                data = json.loads(file_content)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")

    return data


def clear_json():
    empty_data = {}
    with open('users.json', 'w') as file:
        json.dump(empty_data, file, indent=4)


def check_permission_user(interaction: discord.Interaction):
    allowed_users = {792447252424687626, 731075986195611689}
    return interaction.user.id in allowed_users


class TicketDropdown(discord.ui.Select):  # Rückmeldung Server (Nitro Giveaway)

    def __init__(self):
        options = [
            discord.SelectOption(label="Support",
                                 description="Für allgemeine Anliegen und Fragen"),
            discord.SelectOption(
                label="Bewerbung als Spieler in unseren Teams",
                description="Du bewirbst dich als Teammitglied unserer Orga"),
            discord.SelectOption(
                label="Bewerbung als Supporter",
                description=
                "Du bewirbst dich als Teammitglied. Discord Moderator, Social Media Manager, Team-Manager, etc"),
            discord.SelectOption(
                label="Rückmeldung Server (Nitro Giveaway)",
                description=
                "Bitte gebe uns Rückmeldung wie du aktuell SPEX findest und habe die Chance auf Discord Nitro!"
            )
        ]
        super().__init__(
            placeholder='Wähle ein Thema.',
            options=options)

    async def callback(self, interaction: discord.Interaction):
        user_tag = str(interaction.user)
        selected_label = self.values[0]
        channel = interaction.channel
        new_name = f"Ticket-{interaction.user.name}-{selected_label}"

        if selected_label == "Bewerbung als Spieler in unseren Teams":

            role_id = 1164252806123900928
            role = discord.utils.get(interaction.guild.roles, id=role_id)
            if role:
                await interaction.user.add_roles(role)
            else:
                print(f'Rolle mit ID {role_id} nicht gefunden')
            embed = discord.Embed(
                title="Bewerbung als Spieler in unseren Teams",
                description=
                "Bitte beantworte die folgenden Fragen, um deine Bewerbung abzuschließen. Unser Bot wird die Fragen in diesen Chat schreiben. Du musst dann auf diese einf hier antworten. Am Ende werden deine Antworten ausgegeben.:",
                color=discord.Color.blue())
            embed.add_field(name="`Frage 1`",
                            value="**Wie heißt du?** | **Vorname reichte**",
                            inline=False)
            embed.add_field(name="`Frage 2`",
                            value="Deine Links |**Tracker link, steam, etc**",
                            inline=False)
            embed.add_field(name="`Frage 2`", value="Wie alt bist du?", inline=False)
            embed.add_field(name="`Frage 3`",
                            value="Warum möchtest **du** **__Spex__** beitreten?",
                            inline=False)

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            footer_text = f"Erstellt von Hendrik | {timestamp} | Season-3-Bot V1"
            embed.set_footer(text=footer_text)

            await interaction.response.send_message(embed=embed)
            await channel.edit(name=new_name)

            questions = [
                f"Bitte Antworte auf meine Nachrichten {interaction.user.mention}, damit das hier alles schnell geht :D Hast du das verstandnen? (J/J)",
                "**Wie heißt du?** | **Vorname reichte**",
                "**Deine Links |**Tracker link, steam, etc**",
                "**Wie alt bist du?**",
                "Warum möchtest **du** **__Spex__** beitreten?",
            ]

            answers = []

            for question in questions:
                question_msg = await interaction.channel.send(question)

                def check(m):
                    return m.author == interaction.user and m.channel == interaction.channel

                try:
                    message = await bot.wait_for('message', check=check, timeout=120.0)
                    answers.append(message.content)
                    await message.delete()
                    await question_msg.delete()
                except asyncio.TimeoutError:
                    await interaction.channel.send(
                        'Zeitüberschreitung! Bitte starte den Prozess erneut.')
                    return

            result_embed = discord.Embed(
                title="Zusammenfassung der Bewerbung asl Spieler für Spex",
                description="Hier sind Ihre Antworten:",
                color=discord.Color.green())
            for idx, answer in enumerate(answers, 1):
                if len(answer) <= 1024:
                    result_embed.add_field(name=f"`Antwort zu Frage {idx}`",
                                           value=answer,
                                           inline=False)
                else:
                    chunks = [answer[i:i + 1024] for i in range(0, len(answer), 1024)]
                    for j, chunk in enumerate(chunks):
                        result_embed.add_field(
                            name=f"`Antwort zu Frage {idx} (Teil {j + 1})`",
                            value=chunk,
                            inline=False)

                if len(result_embed.fields) >= 25:
                    await interaction.channel.send(embed=result_embed)
                    result_embed = discord.Embed(
                        title=
                        "Zusammenfassung Ihrer Bewerbung für Season 4 (Fortsetzung)",
                        color=discord.Color.green())

            await interaction.channel.send(embed=result_embed)
            return

        elif selected_label == "Bewerbung als Supporter":

            role_id = 1164252806123900928
            role = discord.utils.get(interaction.guild.roles, id=role_id)
            if role:
                await interaction.user.add_roles(role)
            else:
                print(f'Rolle mit ID {role_id} nicht gefunden')
            embed = discord.Embed(
                title="Bewerbung für das Spex Team",
                description=
                "Bitte beantworte die folgenden Fragen, um deine Bewerbung abzuschließen:",
                color=discord.Color.blue())
            embed.add_field(
                name="`Frage 1`",
                value=
                "Welche **Art** von Supporter möchtest du werden | **Discord Moderator, Social Media Manager, Team-Manager, Designer?**",
                inline=False)
            embed.add_field(
                name="`Frage 2`",
                value="Wie heißt du und wie alt bist du? | **Vorname reicht**",
                inline=False)
            embed.add_field(name="`Frage 3`",
                            value="Warum möchtest du ein Teil von uns werden?",
                            inline=False)
            embed.add_field(name="`Frage 4`",
                            value="Was bringst du an Erfahrung mit?",
                            inline=False)
            embed.add_field(name="`Frage 5`",
                            value="Erzähle doch kurz was über dich:eyes:",
                            inline=False)

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            footer_text = f"Erstellt von Hendrik | {timestamp} | Season-3-Bot V1"
            embed.set_footer(text=footer_text)

            await interaction.response.send_message(embed=embed)
            await channel.edit(name=new_name)

            questions = [
                f"Bitte Antworte auf meine Nachrichten {interaction.user.mention}, damit das hier alles schnell geht :D Hast du das verstandnen? (J/J)",
                "**Für welche Rolle bewirbst du dich?** | **(Discord Moderator, Social Media Manager, Team-Manager, Designer)**",
                "**Wie heißt du und wie alt bist du?** | **(Vorname reicht^^)**",
                "**Warum möchtest __DU__ ein Teil von uns werden?**",
                "**Was bringst du an Erfahrung mit?**"
            ]

            answers = []

            for question in questions:
                question_msg = await interaction.channel.send(question)

                def check(m):
                    return m.author == interaction.user and m.channel == interaction.channel

                try:
                    message = await bot.wait_for('message', check=check, timeout=120.0)
                    answers.append(message.content)
                    await message.delete()
                    await question_msg.delete()
                except asyncio.TimeoutError:
                    await interaction.channel.send(
                        'Zeitüberschreitung! Bitte starte den Prozess erneut.')
                    return

            result_embed = discord.Embed(
                title="Zusammenfassung der Bewerbung fpr Spex",
                description="Hier sind Ihre Antworten:",
                color=discord.Color.green())
            for idx, answer in enumerate(answers, 1):
                if len(answer) <= 1024:
                    result_embed.add_field(name=f"`Antwort zu Frage {idx}`",
                                           value=answer,
                                           inline=False)
                else:
                    chunks = [answer[i:i + 1024] for i in range(0, len(answer), 1024)]
                    for j, chunk in enumerate(chunks):
                        result_embed.add_field(
                            name=f"`Antwort zu Frage {idx} (Teil {j + 1})`",
                            value=chunk,
                            inline=False)

                if len(result_embed.fields) >= 25:
                    await interaction.channel.send(embed=result_embed)
                    result_embed = discord.Embed(
                        title=
                        "Zusammenfassung Ihrer Bewerbung für Season 4 (Fortsetzung)",
                        color=discord.Color.green())

            await interaction.channel.send(embed=result_embed)
            return
        elif selected_label == "Rückmeldung Server (Nitro Giveaway)":
            await channel.edit(name=new_name)
            embed = discord.Embed(
                title="Feeback + Chance auf Nitro",
                description=
                "Bitte beantworte die folgenden Fragen, um die Anmeldung für das Giveaway abzuschließen:",
                color=discord.Color.blue())
            embed.add_field(name="`Frage 1`",
                            value="Wie gefällt dir SPEX (1-10)?",
                            inline=False)
            embed.add_field(
                name="`Frage 2`",
                value="Welche Funktionen/neue Chats/Talks/Events wünschst du dir?",
                inline=False)
            embed.add_field(name="`Frage 3`",
                            value="Was würdest du an SPEX verbessern?",
                            inline=False)
            embed.add_field(
                name="`Frage 4`",
                value="Freust du dich auf Season 4? JA/JAAAAA/**SUPERRRR JAAAAAAA**",
                inline=False)

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            footer_text = f"Erstellt von Hendrik | {timestamp} | Season-3-Bot V1"
            embed.set_footer(text=footer_text)

            await interaction.response.send_message(embed=embed)

            questions = [
                f"Bitte Antworte auf meine Nachrichten {interaction.user.mention}, damit das hier alles schnell geht :D Hast du das verstandnen? (J/J)",
                "**Wie gefällt dir SPEX (1-10)?**",
                "**Welche Funktionen/neue Chats/Talks/Events wünschst du dir?**",
                "**Was würdest du an SPEX verbessern?**",
                "**Freust du dich auf Season 4? JA/JAAAAA/**SUPERRRR JAAAAAAA**"
            ]

            answers = []

            for question in questions:
                question_msg = await interaction.channel.send(question)

                def check(m):
                    return m.author == interaction.user and m.channel == interaction.channel

                try:
                    message = await bot.wait_for('message', check=check, timeout=120.0)
                    answers.append(message.content)
                    await message.delete()
                    await question_msg.delete()
                except asyncio.TimeoutError:
                    await interaction.channel.send(
                        'Zeitüberschreitung! Bitte starte den Prozess erneut.')
                    return

            result_embed = discord.Embed(
                title="Zusammenfassung deines Feebacks!",
                description=
                "Hier sind Ihre Antworten **und du hast nun die Chance Nitro zu Gewinnen!:",
                color=discord.Color.green())
            for idx, answer in enumerate(answers, 1):
                if len(answer) <= 1024:
                    result_embed.add_field(name=f"`Antwort zu Frage {idx}`",
                                           value=answer,
                                           inline=False)
                else:
                    chunks = [answer[i:i + 1024] for i in range(0, len(answer), 1024)]
                    for j, chunk in enumerate(chunks):
                        result_embed.add_field(
                            name=f"`Antwort zu Frage {idx} (Teil {j + 1})`",
                            value=chunk,
                            inline=False)

                if len(result_embed.fields) >= 25:
                    await interaction.channel.send(embed=result_embed)
                    result_embed = discord.Embed(
                        title=
                        "Zusammenfassung Ihrer Bewerbung für Season 4 (Fortsetzung)",
                        color=discord.Color.green())

            await interaction.channel.send(embed=result_embed)
            save_user_to_json(user_tag)
            return
        else:
            await channel.edit(name=new_name)
            embed = discord.Embed(
                title="**Genereller Support**",
                description=
                "Bitte habe etwas **Geduld**! Jemand aus unserem Team wird sich **gleich bei dir melden**! **Beschreibe** doch schonmal **dein Anliegen**, damit **wir dir** besser helfen können",
                color=discord.Color.blue())

        timestamp = datetime.datetime.now().strftime("%Y-%m-%"
                                                     "d %H:%M:%S")
        footer_text = f"Erstellt von Hendrik | {timestamp} | Season-3-Bot V1"
        embed.set_footer(text=footer_text)

        await interaction.response.send_message(embed=embed)

        return

    class TicketView(discord.ui.View):

        def __init__(self):
            super().__init__()
            self.add_item(TicketButton(label='Ticket erstellen'))

    class TicketButton(discord.ui.Button):

        def __init__(self, label):
            super().__init__(style=discord.ButtonStyle.primary, label=label)

        async def callback(self, interaction: discord.Interaction):
            user_id = str(interaction.user.id)
            tickets = load_tickets()

            if user_id in tickets and tickets[user_id]['status'] == 'open':
                await interaction.response.send_message("Du hast bereits ein Ticket!",
                                                        ephemeral=True)
                return

            channel_name = f"ticket-{interaction.user.name.lower()}"

            tickets[user_id] = {
                "ticket_id": channel_name,
                "user_id": user_id,
                "user_name": interaction.user.name,
                "status": "open"
            }
            save_tickets(tickets)

            category = discord.utils.get(interaction.guild.categories,
                                         name=TICKET_CATEGORY_NAME)
            if not category:
                category = await interaction.guild.create_category(TICKET_CATEGORY_NAME
                                                                   )

            overwrites = {
                interaction.guild.default_role:
                    discord.PermissionOverwrite(read_messages=False),
                interaction.guild.me:
                    discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.user:
                    discord.PermissionOverwrite(read_messages=True,
                                                send_messages=True,
                                                manage_messages=True,
                                                manage_channels=True)
            }

            helper_role = discord.utils.get(interaction.guild.roles,
                                            name=HELPER_ROLE_NAME)
            if helper_role:
                overwrites[helper_role] = discord.PermissionOverwrite(
                    read_messages=True, send_messages=True)

            special_role_ids = [
                1167467842795470878, 1163855249585483926, 1161642740094881802
            ]
            for role_id in special_role_ids:
                special_role = interaction.guild.get_role(role_id)
                if special_role:
                    overwrites[special_role] = discord.PermissionOverwrite(
                        read_messages=True, send_messages=True)

            ticket_channel = await category.create_text_channel(
                channel_name, overwrites=overwrites)
            ticket_voice_channel = await category.create_voice_channel(
                f"{channel_name}-voice", overwrites=overwrites)

            ticket_holders.add(user_id)

            embed = discord.Embed(
                title="Willkommen im Support-Ticket",
                description=
                f"Hallo {interaction.user.mention}, wir haben dir diesen Text Channel sowie einen voice channel erstellt. Hier wird dir jemand aus unserem Team in kürze helfen. Bitte habe etwas gedult, da wir nicht 24/7 erreichbar sind. Vielen dank für dein verständniss!",
                color=discord.Color.blue())

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            footer_text = f"Erstellt von Hendrik | {timestamp} | Season-3-Bot V1"
            embed.set_footer(text=footer_text)

            close_ticket_view = discord.ui.View()
            close_ticket_view.add_item(CloseTicketButton())

            await ticket_channel.send(embed=embed, view=close_ticket_view)

            embed = discord.Embed(
                title="Ticket-Thema Auswahl",
                description="Bitte wählen Sie ein Thema für Ihr Ticket:",
                color=discord.Color.blue())

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            footer_text = f"Erstellt von Hendrik | {timestamp} | Season-3-Bot V1"
            embed.set_footer(text=footer_text)

            dropdown = TicketDropdown()
            view = discord.ui.View()
            view.add_item(dropdown)
            await ticket_channel.send(embed=embed, view=view)

            await interaction.response.send_message(
                f"Ihr Ticket wurde erstellt: {ticket_channel.mention}",
                ephemeral=True)

            return


class TicketView(discord.ui.View):

    def __init__(self):
        super().__init__()
        self.add_item(TicketButton(label='Ticket erstellen'))


class TicketButton(discord.ui.Button):

    def __init__(self, label):
        super().__init__(style=discord.ButtonStyle.primary, label=label)

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        tickets = load_tickets()

        if user_id in tickets and tickets[user_id]['status'] == 'open':
            await interaction.response.send_message("Du hast bereits ein Ticket!",
                                                    ephemeral=True)
            return

        channel_name = f"ticket-{interaction.user.name.lower()}"

        tickets[user_id] = {
            "ticket_id": channel_name,
            "user_id": user_id,
            "user_name": interaction.user.name,
            "status": "open"
        }
        save_tickets(tickets)

        category = discord.utils.get(interaction.guild.categories,
                                     name=TICKET_CATEGORY_NAME)
        if not category:
            category = await interaction.guild.create_category(TICKET_CATEGORY_NAME)

        overwrites = {
            interaction.guild.default_role:
                discord.PermissionOverwrite(read_messages=False),
            interaction.guild.me:
                discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user:
                discord.PermissionOverwrite(read_messages=True,
                                            send_messages=True,
                                            manage_messages=True,
                                            manage_channels=True)
        }

        helper_role = discord.utils.get(interaction.guild.roles,
                                        name=HELPER_ROLE_NAME)
        if helper_role:
            overwrites[helper_role] = discord.PermissionOverwrite(read_messages=True,
                                                                  send_messages=True)

        special_role_ids = [
            1167467842795470878, 1163855249585483926, 1161642740094881802
        ]
        for role_id in special_role_ids:
            special_role = interaction.guild.get_role(role_id)
            if special_role:
                overwrites[special_role] = discord.PermissionOverwrite(
                    read_messages=True, send_messages=True)

        ticket_channel = await category.create_text_channel(channel_name,
                                                            overwrites=overwrites)
        ticket_voice_channel = await category.create_voice_channel(
            f"{channel_name}-voice", overwrites=overwrites)

        ticket_holders.add(user_id)

        embed = discord.Embed(
            title="Willkommen im Support-Ticket",
            description=
            f"Hallo {interaction.user.mention}, wir haben dir diesen Text Channel sowie einen Voice-Channel erstellt. Hier wird dir jemand aus unserem Team in Kürze helfen. Bitte habe etwas Geduld, da wir nicht 24/7 erreichbar sind. Vielen dank für dein Verständniss!",
            color=discord.Color.blue())

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        footer_text = f"Erstellt von Hendrik | {timestamp} | Season-3-Bot V1"
        embed.set_footer(text=footer_text)

        close_ticket_view = discord.ui.View()
        close_ticket_view.add_item(CloseTicketButton())

        await ticket_channel.send(embed=embed, view=close_ticket_view)

        embed = discord.Embed(
            title="Ticket-Thema Auswahl",
            description="Bitte wähle ein Thema für das Ticket:",
            color=discord.Color.blue())

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        footer_text = f"Erstellt von Hendrik | {timestamp} | Season-3-Bot V1"
        embed.set_footer(text=footer_text)

        dropdown = TicketDropdown()
        view = discord.ui.View()
        view.add_item(dropdown)
        await ticket_channel.send(embed=embed, view=view)

        await interaction.response.send_message(
            f"Ihr Ticket wurde erstellt: {ticket_channel.mention}", ephemeral=True)


class CloseTicketButton(discord.ui.Button):

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.danger,
                         label='Ticket schließen')

    def user_can_close_ticket(self, interaction, channel):
        user_ticket_prefix = f"ticket-{interaction.user.name.lower()}"
        specific_role_ids = (1167467842795470878, 1163855249585483926,
                             1161642740094881802, 1164252806123900928,
                             1163855249585483926)
        has_specific_role = any(
            discord.utils.get(interaction.user.roles, id=role_id)
            for role_id in specific_role_ids)
        is_ticket_channel = channel.name.startswith(user_ticket_prefix)
        is_helper = any(role.name == HELPER_ROLE_NAME
                        for role in interaction.user.roles)

        return is_ticket_channel or has_specific_role or is_helper

    async def callback(self, interaction: discord.Interaction):
        channel = interaction.channel
        user_ticket_prefix = f"ticket-{interaction.user.name.lower()}"

        if self.user_can_close_ticket(interaction, channel):
            await self.close_ticket(interaction, user_ticket_prefix)
        else:
            await interaction.response.send_message(
                "Du hast keine Berechtigung, dieses Ticket zu schließen!",
                ephemeral=True)

    async def close_ticket(self, interaction, user_ticket_prefix):
        specific_role_ids = (1167467842795470878, 1163855249585483926,
                             1161642740094881802, 1164252806123900928,
                             1163855249585483926)
        has_specific_role = any(
            discord.utils.get(interaction.user.roles, id=role_id) is not None
            for role_id in specific_role_ids)

        for guild_channel in interaction.guild.channels:
            if has_specific_role and guild_channel.name.startswith(
                    user_ticket_prefix):
                ticket_owner_name = guild_channel.name.split('-')[1]
                ticket_owner = discord.utils.get(guild_channel.guild.members,
                                                 name=ticket_owner_name)
                role_id = 1164252806123900928  # Ersetzen Sie dies durch die tatsächliche ID Ihrer Rolle
                role = discord.utils.get(interaction.guild.roles, id=role_id)

                user_id = str(ticket_owner.id)
                tickets = load_tickets()

                if user_id in tickets:
                    tickets[user_id]['status'] = 'closed'
                    save_tickets(tickets)

                await guild_channel.delete()

                if role and ticket_owner:
                    await ticket_owner.remove_roles(role)
                elif not role:
                    print(f'Rolle mit ID {role_id} nicht gefunden')
                elif not ticket_owner:
                    print(f'Ticket-Besitzer {ticket_owner_name} nicht gefunden')
            else:
                print(
                    f'Benutzer {interaction.user} hat nicht die erforderliche Rolle, um Tickets zu schließen.'
                )


class TeamButton(discord.ui.Button):

    def __init__(self, label, embed):
        super().__init__(style=discord.ButtonStyle.primary, label=label)
        self.embed = embed

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        try:
            await user.send(embed=self.embed)
            await interaction.response.send_message(
                "Ein Embed wurde als DM gesendet.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message(
                "Es konnte keine DM gesendet werden. Möglicherweise hat der Benutzer DMs von Servermitgliedern blockiert.",
                ephemeral=True)


class TeamView(discord.ui.View):

    def __init__(self):
        super().__init__()
        spieler_liste_1 = [
            "[HelloThere](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)",
            "[HelloThere](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)",
            "[HelloThere](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)",
            "[HelloThere](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)",
            "[HelloThere](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)"
        ]

        spieler_liste_2 = [
            "[HelloThere2](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)",
            "[HelloThere2](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)",
            "[HelloThere2](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)",
            "[HelloThere2](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)",
            "[HelloThere2](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)"
        ]

        spieler_liste_3 = [
            "[HelloThere3](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)",
            "[HelloThere3](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)",
            "[HelloThere3](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)",
            "[HelloThere3](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)",
            "[HelloThere3](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)"
        ]

        spieler_liste_4 = [
            "[HelloThere4](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)",
            "[HelloThere4](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)",
            "[HelloThere4](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)",
            "[HelloThere4](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)",
            "[HelloThere4](https://tracker.gg/valorant/profile/riot/HelloThere%23Shine/overview)"
        ]

        embed_team1 = discord.Embed(title="Team Informationen:", color=0x3498db)
        embed_team1.add_field(name="Team", value="Main Team", inline=False)

        for idx, spieler in enumerate(spieler_liste_1, start=1):
            embed_team1.add_field(name=f"Spieler {idx}", value=spieler, inline=False)

        embed_team1.add_field(name="Trainer", value="HelloThere", inline=False)
        embed_team1.add_field(
            name="Kurze Zusammenfassung",
            value=
            "dfkljshgsdkljfhslkjdhlkjhlkjsdghlkdjshgdkljghlkdsjhgkljdhgkldhglkdhglkdhglkdjghdlksjghdlkghfdlkgfhdlkgjhhjkdsjhkdfgjkgdfdfkljshgsdkljfhslkjdhlkjhlkjsdghlkdjshgdkljghlkdsjhgkljdhgkldhglkdhglkdhglkdjghdlksjghdlkghfdlkgfhdlkgjhhjkdsjhkdfgjkgdf",
            inline=False)
        embed_team1.add_field(name="Bewerbung offen",
                              value="Ja/Nein",
                              inline=False)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        footer_text = f"Erstellt von Hendrik | {timestamp} | Season-3-Bot V1"
        embed_team1.set_footer(text=footer_text)

        self.add_item(TeamButton(label='[team name]', embed=embed_team1))
        # --------------------------------------------------------------------------------------
        embed_team2 = discord.Embed(title="Team Informationen:", color=0x3498db)
        embed_team2.add_field(name="Team", value="Contax", inline=False)

        for idx, spieler in enumerate(spieler_liste_2, start=1):
            embed_team2.add_field(name=f"Spieler {idx}", value=spieler, inline=False)

        embed_team2.add_field(name="Trainer", value="HelloThere", inline=False)
        embed_team2.add_field(
            name="Kurze Zusammenfassung",
            value=
            "dfkljshgsdkljfhslkjdhlkjhlkjsdghlkdjshgdkljghlkdsjhgkljdhgkldhglkdhglkdhglkdjghdlksjghdlkghfdlkgfhdlkgjhhjkdsjhkdfgjkgdfdfkljshgsdkljfhslkjdhlkjhlkjsdghlkdjshgdkljghlkdsjhgkljdhgkldhglkdhglkdhglkdjghdlksjghdlkghfdlkgfhdlkgjhhjkdsjhkdfgjkgdf",
            inline=False)
        embed_team2.add_field(name="Bewerbung offen",
                              value="Ja/Nein",
                              inline=False)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        footer_text = f"Erstellt von Hendrik | {timestamp} | Season-3-Bot V1"
        embed_team2.set_footer(text=footer_text)

        self.add_item(TeamButton(label='[team name]', embed=embed_team2))
        # -------------------------------------------------------------------------------------------
        embed_team3 = discord.Embed(title="Team Informationen:", color=0x3498db)
        embed_team3.add_field(name="Team", value="Contax", inline=False)

        for idx, spieler in enumerate(spieler_liste_3, start=1):
            embed_team3.add_field(name=f"Spieler {idx}", value=spieler, inline=False)

        embed_team3.add_field(name="Trainer", value="HelloThere", inline=False)
        embed_team3.add_field(
            name="Kurze Zusammenfassung",
            value=
            "dfkljshgsdkljfhslkjdhlkjhlkjsdghlkdjshgdkljghlkdsjhgkljdhgkldhglkdhglkdhglkdjghdlksjghdlkghfdlkgfhdlkgjhhjkdsjhkdfgjkgdfdfkljshgsdkljfhslkjdhlkjhlkjsdghlkdjshgdkljghlkdsjhgkljdhgkldhglkdhglkdhglkdjghdlksjghdlkghfdlkgfhdlkgjhhjkdsjhkdfgjkgdf",
            inline=False)
        embed_team3.add_field(name="Bewerbung offen",
                              value="Ja/Nein",
                              inline=False)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        footer_text = f"Erstellt von Hendrik | {timestamp} | Season-3-Bot V1"
        embed_team3.set_footer(text=footer_text)

        self.add_item(TeamButton(label='[team name]', embed=embed_team3))
        #  ------------------------------------------------------------------------------------------
        embed_team4 = discord.Embed(title="Team Informationen:", color=0x3498db)

        embed_team4.add_field(name="Team", value="Contax", inline=False)

        for idx, spieler in enumerate(spieler_liste_4, start=1):
            embed_team4.add_field(name=f"Spieler {idx}", value=spieler, inline=False)

        embed_team4.add_field(name="Trainer", value="HelloThere", inline=False)
        embed_team4.add_field(
            name="Kurze Zusammenfassung",
            value=
            "dfkljshgsdkljfhslkjdhlkjhlkjsdghlkdjshgdkljghlkdsjhgkljdhgkldhglkdhglkdhglkdjghdlksjghdlkghfdlkgfhdlkgjhhjkdsjhkdfgjkgdfdfkljshgsdkljfhslkjdhlkjhlkjsdghlkdjshgdkljghlkdsjhgkljdhgkldhglkdhglkdhglkdjghdlksjghdlkghfdlkgfhdlkgjhhjkdsjhkdfgjkgdf",
            inline=False)
        embed_team4.add_field(name="Bewerbung offen",
                              value="Ja/Nein",
                              inline=False)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        footer_text = f"Erstellt von Hendrik | {timestamp} | Season-3-Bot V1"
        embed_team4.set_footer(text=footer_text)

        self.add_item(TeamButton(label='[team name]', embed=embed_team4))


#  ------------------------------------------------------------------------------------------


@bot.tree.command(name="createticket",
                  description="Erstelle ein neues Support-Ticket.")
async def createticket(interaction: discord.Interaction):
    if PERMISSION_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message(
            "Du hast keine Berechtigung, diesen Befehl auszuführen.",
            ephemeral=True)
        return

    embed = discord.Embed(
        title="Create a Ticket",
        description=
        "Erstelle ein Ticket und wähle danach in deinem Ticket das Thema aus! Bitte befolge dabei alle Schritte und Informationen vom Bot! Vielen Dank^^",
        color=discord.Color.blue())
    embed.add_field(
        name="**AKTUELLER BUG**",
        value=
        "**Durch einen Bug kann nur der User das Ticket schließen, welcher auch das Ticket eröffnet hat. Ich bin aktuell dabei dies zu beheben!**",
        inline=False)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    footer_text = f"Erstellt von Hendrik | {timestamp} | Season-3-Bot V1"
    embed.set_footer(text=footer_text)

    await interaction.response.send_message(embed=embed, view=TicketView())


@bot.tree.command(name="giveaway_end")
async def random_user(interaction: discord.Interaction):
    if not (check_permission_user(interaction)
            or interaction.user.guild_permissions.administrator):
        await interaction.response.send_message(
            'Du hast keine Berechtigung, diesen Befehl zu verwenden.',
            ephemeral=True)
        returnF

    data = load_data_from_json()
    if not data:
        await interaction.response.send_message("Keine Benutzer gefunden.",
                                                ephemeral=True)
        return

    random_user_id = random.choice(list(data.keys()))
    winner_mention = f"**__{random_user_id}__**"

    embed = discord.Embed(title="🎉 Gewinnspiel-Ergebnisse 🎉",
                          description=(f"{winner_mention} ist der winner"),
                          color=discord.Color.blue())

    embed.set_footer(text="Bleibt dran für zukünftige Gewinnspiele und Events!")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="cleargiveaway")
async def clear_giveaway(interaction: discord.Interaction):
    if check_permission_user(
            interaction or interaction.user.guild_permissions.administrator):
        clear_json()
        await interaction.response.send_message(
            'Die Giveaway-Daten wurden erfolgreich zurückgesetzt.', ephemeral=True)
    else:
        await interaction.response.send_message(
            'Du hast keine Berechtigung, diesen Befehl zu verwenden.',
            ephemeral=True)


@bot.tree.command(
    name="announce",
    description="Mache eine Ankündigung in einer eingebetteten Nachricht.")
async def announce(
        interaction: discord.Interaction,
        message: str,
        field1_name: str = None,
        field1_value: str = None,
        field2_name: str = None,
        field2_value: str = None,
        field3_name: str = None,
        field3_value: str = None,
        field4_name: str = None,
        field4_value: str = None,
        field5_name: str = None,
        field5_value: str = None,
        field6_name: str = None,
        field6_value: str = None,
):
    if PERMISSION_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message(
            "Du hast keine Berechtigung, diesen Befehl auszuführen.",
            ephemeral=True)
        return

    embed = discord.Embed(title="Ankündigung",
                          description=message,
                          color=discord.Color.blue())

    if field1_name and field1_value:
        embed.add_field(name=field1_name, value=field1_value)

    if field2_name and field2_value:
        embed.add_field(name=field2_name, value=field2_value)

    if field3_name and field3_value:
        embed.add_field(name=field3_name, value=field3_value)

    if field4_name and field4_value:
        embed.add_field(name=field4_name, value=field4_value)

    if field5_name and field5_value:
        embed.add_field(name=field5_name, value=field5_value)

    if field6_name and field6_value:
        embed.add_field(name=field6_name, value=field6_value)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    footer_text = f"Erstellt von Hendrik | {timestamp} | Season-3-Bot V1"
    embed.set_footer(text=footer_text)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(
    name="spex",
    description="Mache eine Ankündigung in einer eingebetteten Nachricht.")
async def spex(interaction: discord.Interaction):
    embed = discord.Embed(title="**About SPEX**", color=discord.Color.blue())

    embed.add_field(
        name="**__*Was ist SPEX?*__**",
        value=
        "*__SPEX__* ist eine am *13.10.2023* gegründete eSport Organisation, die sich ausschließlich auf das Spiel 'Valorant' konzentriert. "
        "Wir konzentrieren uns sowohl auf __Low-__, als auch __High-Elo Valorant Teams__ und wollen mit 3 Rahmenpunkten einen _Safe-Place_ im Internet stellen. "
        "Wir möchten Platz für Spieler schaffen, die in Teams spielen wollen, eine Möglichkeit kreieren, um neue Freundschaften entstehen zu lassen und für gemeinsame und stetige Verbesserung sorgen, wobei der zwischenmenschliche und spielerische Aspekt gemeint ist.",
        inline=False)

    embed.add_field(
        name="**Wie ist SPEX aufgebaut?**",
        value=
        "__SPEX besteht vorläufig aus 4 Teams__, bei denen 3 Community Teams sind und letzteres ein High-Elo Team ist.",
        inline=False)

    embed.add_field(
        name="**Main Team (Ascendant-Immortal)**",
        value="<@&1168297945284755546> Main Team **=> Edit Role ID**",
        inline=False)

    embed.add_field(
        name="**Community Teams (Gold-Dia)**",
        value=
        "<@&1168297945284755546> Contact **=> Edit Role ID**\n<@&1168297945284755546> Recon **=> Edit Role ID**\n<@&1168297945284755546> Nova **=> Edit Role ID**",
        inline=False)

    embed.add_field(
        name="**Wie kann ich mich bewerben?**",
        value=
        "*Im Channel <#1090747275933921292> **=> Edit channel ID** | support* ist ein __Bewerbungs- und Supportticketsystem__ vorhanden. Nach der Bewerbung werden wir dich einem Team für die *Tryoutphase* zuordnen.",
        inline=False)

    embed.add_field(
        name="**__*Die Buttons daunten...*__**",
        value=
        "*Klicke auf die __untenstehenden Buttons__, um nähere Informationen zu den jeweiligen Teams zu erhalten.*",
        inline=False)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    footer_text = f"Erstellt von Hendrik | {timestamp} | Season-3-Bot V1"
    embed.set_footer(text=footer_text)

    await interaction.response.send_message(embed=embed, view=TeamView())


@bot.event
async def on_ready():
    print(f'Bot ist eingeloggt als {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

bot.run(Token)
