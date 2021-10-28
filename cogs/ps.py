import discord

from discord.ext import commands
import asyncio
import traceback
import datetime
import sys
import re
import json
from discord_components import DiscordComponents, Button, Select, SelectOption, ActionRow


class PS(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        with open('config.json') as config_file:
            config = json.load(config_file)

        if len(config['GLOBAL_PREFIX']) != 0:
            self.unit = config["UNIT_TEXT"]
        else:
            self.unit = "[Insert Unit Here]"

        try:
            with open("cohort.json", "r", encoding="utf-8") as cohort_file:
                self.cohorts = json.load(cohort_file)
        except:
            try:
                with open("cohort.json", "x", encoding="utf-8") as cohort_file:
                    self.cohorts = {}
                    json.dump(self.cohorts, cohort_file, indent=4)
                print("Created new empty cohort.json file.")
            except Exception as e:
                print(e)
                pass

    def insert_ps(ctx, ps_am, ps_pm,name,am_status,pm_status):
        print(f'Doing for {name}: {am_status} | {pm_status}')
        common_ps = "P|LL|UL|OL|CCL|UCCL|DUTY|VRS|D|GD|DR|AO|OS|RSI|RSO|MA|MC|HL|H|CSE|WFH|QO|OFF"
        common_ps = common_ps.split("|")
        leave_type = ["ll","ol", "ul","cl", "ccl", "uccl"]
        #AM Status
        if re.search(r'[()]',am_status):
            cur_status = am_status.split("(")[0].strip()
            status_date = " (" + "(".join(am_status.split("(")[1:]).strip()
        else:
            cur_status = am_status.strip()
            status_date = ""
        if cur_status.lower() in leave_type:
            cur_status = "LL/OL/UL/CL"
        elif "vrs" in cur_status.lower():
            cur_status = "DUTY"
            status_date = " (VRS)"

        #Alpha: Attempting to handle cases without brackets.
        if len(cur_status.split(" ")) > 1:
            least_index = 9999 #High number to start with
            least_ps = ""
            for possible_ps in common_ps:
                index = cur_status.upper().find(f'{possible_ps} ')
                if index != -1 and index < least_index:
                    print(f'insertps: Found "{possible_ps}" at index "{index}" for "{cur_status}"')
                    least_index = index
                    least_ps = possible_ps
            if least_index < 9999:
                status_date = f' ({cur_status[least_index+len(possible_ps):].strip()})'
                cur_status = cur_status[0:least_index+len(possible_ps)].strip()

        print("AM: {} | {}".format(cur_status, status_date))
        if cur_status.upper() not in ps_am:
            ps_am[cur_status.upper()] = {
                "names": {
                    name.strip(): status_date.strip()
                }
            }
        else:
            ps_am[cur_status.upper()]["names"][name.strip()] = status_date.strip()

        #PM Status
        if re.search(r'[()]',pm_status):
            cur_status = pm_status.split("(")[0].strip()
            status_date = " (" + "(".join(pm_status.split("(")[1:]).strip()
        else:
            cur_status = pm_status.strip()
            status_date = ""
        if cur_status.lower() in leave_type:
            cur_status = "LL/OL/UL/CL"
        elif "vrs" in cur_status.lower():
            cur_status = "DUTY"
            status_date = " (VRS)"
        #Alpha: Attempting to handle cases without brackets.
        if len(cur_status.split(" ")) > 1:
            least_index = 9999 #High number to start with
            least_ps = ""
            for possible_ps in common_ps:
                index = cur_status.upper().find(f'{possible_ps} ')
                if index != -1 and index < least_index:
                    print(f'insertps: Found "{possible_ps}" at index "{index}" for "{cur_status}"')
                    least_index = index
                    least_ps = possible_ps
            if least_index < 9999:
                status_date = f' ({cur_status[least_index+len(possible_ps):].strip()})'
                cur_status = cur_status[0:least_index+len(possible_ps)].strip()
        print("PM: {} | {}".format(cur_status, status_date))
        if cur_status.upper() not in ps_pm:
            ps_pm[cur_status.upper()] = {
                "names": {
                    name.strip(): status_date.strip()
                }
            }
        else:
            ps_pm[cur_status.upper()]["names"][name.strip()] = status_date.strip()

    @commands.command(brief='Delete an existing Cohort Group', name="deletecohort", aliases=['delcohort'])
    async def deletecohort(self, ctx, *, cohort_name):
        """
        If no cohort group is found, an error will be shown. This command is irreversible!
        """
        def check(res):
            return res.user == ctx.author and res.message == msg

        if cohort_name.lower() in [x.lower() for x in self.cohorts]: #case-insensitive matching
            #We need to case sensitive name to do stuff properly, so this is a dumb way of correcting casing
            for x in self.cohorts:
                if cohort_name.lower() == x.lower():
                    cohort_name = x
                    break

            msg = await ctx.reply(
                embed=discord.Embed(
                    title=f"Are you sure you want to delete Cohort Group `{cohort_name}`? **This change is irreversible!**",
                    colour=0xff0000,
                ),
                components = [
                    [
                        Button(label = "✓ Yes", style="3", custom_id = "yes"),
                        Button(label = "❌ No", style="4", custom_id = "no")
                    ]
                ]
            )
            try:
                selected_button = await self.bot.wait_for("button_click", check=check, timeout=30)
                if selected_button.custom_id == "yes":
                    del self.cohorts[cohort_name]
                    with open('cohort.json', 'w', encoding='utf-8') as cohort_file:
                        json.dump(self.cohorts, cohort_file, indent=4)
                    await ctx.reply(embed=discord.Embed(title=f"Successfully deleted cohort group `{cohort_name}`.", colour=0x00ff00))

                elif selected_button.custom_id == "no":
                    await ctx.reply(embed=discord.Embed(title=f"No changes were made to cohort group {cohort_name}. Command cancelled.", colour=0xff0000))

                await msg.edit(embed=discord.Embed(
                        title=f"Are you sure you want to delete Cohort Group `{cohort_name}`? **This change is irreversible!**",
                        colour=0xff0000,
                    ),
                    components = [
                        [
                            Button(label = "✓ Yes", style="3", custom_id = "yes", disabled=True),
                            Button(label = "❌ No", style="4", custom_id = "no", disabled=True)
                        ]
                    ]
                )
                await selected_button.respond(type=7)
            except asyncio.TimeoutError:
                await msg.edit(
                    embed=discord.Embed(
                            title=f"Are you sure you want to delete Cohort Group `{cohort_name}`? **This change is irreversible!**",
                            colour=0xff0000,
                        ),
                    components=[
                        Button(style=4, label="⧗ Timed out!", disabled=True),
                    ],
                )
        else:
            await ctx.reply(embed=discord.Embed(title=f"Could not find Cohort Group `{cohort_name}`. Did you make a typo?", colour=0xff0000))
        return


    @commands.command(brief='Set/Edit a Cohort Group',name='setcohort')
    async def setcohort(self, ctx, *, cohort_name = None):
        """
        Create or change a Cohort Group. Please remember to separate names using a new line.
        """
        if cohort_name is None or cohort_name.lower() == "list":
            list_cohort = ""
            for cohort in self.cohorts:
                list_cohort += "**{}**\n{}\n\n".format(cohort, "\n".join([name.title() for name in self.cohorts[cohort]]))
            if len(list_cohort) < 2000:
                await ctx.reply(list_cohort, mention_author=False)
            else: #Total message length is longer than Discord allowed, hence we're splitting it up.
                start_index = 0
                message2send = list_cohort
                while start_index < len(message2send):
                    await ctx.send(message2send[start_index:start_index + 2000])
                    start_index = start_index + 2000
            return
        else:
            if cohort_name.lower() in [x.lower() for x in self.cohorts]: #case-insensitive matching

                #We need to case sensitive name to do stuff properly, so this is a dumb way of correcting casing
                for x in self.cohorts:
                    if cohort_name.lower() == x.lower():
                        cohort_name = x
                        break

                await ctx.reply(f"You're now editing the namelist for Cohort Group `{cohort_name}`. The current namelist is outputted below, please copy the names and edit/add/remove names, then send the updated list. Separate names by using a newline (one name per line). This command will timeout in 5 minutes. Reply `cancel` to cancel command.")
                await ctx.send("\n".join([name.title() for name in self.cohorts[cohort_name]]))
                try:
                    cohort_namelist_msg = await self.bot.wait_for('message', check = lambda m: m.author == ctx.author, timeout=300)
                except asyncio.TimeoutError:
                    await ctx.send("Command timeout.")
                    return
                if cohort_namelist_msg.content == "cancel":
                    await ctx.send("Command Cancelled.")
                    return
                cohort_namelist = [name.strip().lower() for name in cohort_namelist_msg.content.split("\n")]
                removed_names = list(set(self.cohorts[cohort_name]) - set(cohort_namelist))
                added_names = list(set(cohort_namelist) - set(self.cohorts[cohort_name]))

                await cohort_namelist_msg.reply("Changes made to `{}`:\n**Removed Names**:\n{}\n\n**Added Names**:\n{}\n\n\n**Are you sure you want to proceed**? Reply `y` to proceed or `n` to cancel.".format(cohort_name, '\n'.join([name.title() for name in removed_names]), '\n'.join([name.title() for name in added_names])))
                try:
                    cfm = await self.bot.wait_for('message', check = lambda m: m.author == ctx.author, timeout=30)
                except asyncio.TimeoutError:
                    await ctx.send("Command timeout.")
                    return
                if cfm.content == 'y':
                    self.cohorts[cohort_name] = cohort_namelist
                    with open('cohort.json', 'w', encoding='utf-8') as cohort_file:
                        json.dump(self.cohorts, cohort_file, indent=4)
                    await cfm.reply(f"Successfully amended for cohort group `{cohort_name}`.")
                else:
                    await cfm.reply(f"No changes were made to cohort group {cohort_name}. Command cancelled.", mention_author=False)
                return

            else:
                await ctx.reply(f"You're now creating the namelist for Cohort Group `{cohort_name}`. Please input the namelist, and separate names by using a newline (one name per line). This command will timeout in 5 minutes.Reply `cancel` to cancel command.")
                try:
                    cohort_namelist_msg = await self.bot.wait_for('message', check = lambda m: m.author == ctx.author, timeout=300)
                except asyncio.TimeoutError:
                    await ctx.send("Command timeout.")
                    return

                if cohort_namelist_msg.content == "cancel":
                    await ctx.send("Command Cancelled.")
                    return
                cohort_namelist = [name.strip().lower() for name in cohort_namelist_msg.content.split("\n")]

                await cohort_namelist_msg.reply("Please confirm the namelist for Cohort Group `{}` below:\n{}\n\n\n**Are you sure you want to proceed**? Reply `y` to proceed or `n` to cancel.".format(cohort_name, "\n".join([f'{n}. {name.title()}' for n, name in enumerate(cohort_namelist, start=1)])))
                try:
                    cfm = await self.bot.wait_for('message', check = lambda m: m.author == ctx.author, timeout=30)
                except asyncio.TimeoutError:
                    await ctx.send("Command timeout.")
                    return
                if cfm.content == 'y':
                    self.cohorts[cohort_name] = cohort_namelist
                    with open('cohort.json', 'w', encoding='utf-8') as cohort_file:
                        json.dump(self.cohorts, cohort_file, indent=4)
                    await cfm.reply(f"Successfully amended for cohort group `{cohort_name}`.")
                else:
                    await cfm.reply(f"No changes were made to cohort group {cohort_name}. Command cancelled.")
                return


    @commands.command(brief='Craft your Combined Parade State message',name='cos')
    async def cos(self, ctx, debug = "false"):
        """
        You're welcome for this time-saver command. As much as possible, this command will detect the parade states automatically, but do double check before sending it! I will not be held responsible for any wrong parade states.
        """
        await ctx.send("Please send the Regulars Parade State:")
        try:
            regps = await self.bot.wait_for('message', timeout=90, check=lambda message: message.author == ctx.author) #this will be raw text
        except asyncio.TimeoutError:
            await ctx.send("Command timeout.")
            return

        await ctx.send("Please send the NSF Parade State:")
        try:
            nsfps = await self.bot.wait_for('message', timeout=90, check=lambda message: message.author == ctx.author) #this will be raw text
        except asyncio.TimeoutError:
            await ctx.send("Command timeout.")
            return

        error_names = "These people are not added into the Parade State and the total count as I couldn't detect the state. Please manually insert these people into AM/PM parade state and edit the numbers:"

        #setup
        common_ps = "P|LL|UL|OL|CCL|UCCL|DUTY|VRS|D|GD|DR|AO|OS|RSI|RSO|MA|MC|HL|H|CSE|WFH|QO|OFF"
        common_ps = common_ps.split("|")
        #Sort Regulars
        reg_am = {}
        reg_pm = {}

        reg_lines = regps.content.split("\n") #Split into lines
        reg_lines = [line for line in reg_lines if len(line.strip())] #Remove lines with only white-spaces / newlines

        for n, line in enumerate(reg_lines):
            if re.search(r'^P',line) and not re.search(r'^P[a-z]',line): #Finds the Absent line
                present = n #index of "A"
            if re.search(r'^A',line) and not re.search(r'^A[a-z]',line): #Finds the Absent line
                absent = n #index of "A"

        for line_no, line in enumerate(reg_lines):
            name = "" #Reset
            status = "" #Reset
            line = re.sub(r'[*]', '', line) #Remove * in the line
            if line_no == 0: # First line
                date = line[-8:] # Grabs last 8 characters from the line
                print("Date: {}".format(date))
                continue #We done here, move on
            if line == self.unit[-3:] or line_no == present or line_no == absent or line == "":
                continue #Nothing to do here
            if line_no > present and line_no < absent: # Present people
                print(line)
                #Alpha: Attempting to split with and without '-'
                if re.search(r' - ',line):
                    name = line.split(" - ")[0]
                    status = " - ".join(line.split(" - ")[1:])
                else:
                    least_index = 9999 #High number to start with
                    for possible_ps in common_ps:
                        index = line.upper().find(f' {possible_ps}')
                        if index + len(possible_ps) + 1 != len(line): #For those that end with the status. E.g. "XYZ VRS", else we will reject this (e.g. "Ah Haut VRS" detected status will be "H" instead of "VRS")
                            index = -1
                        if index == -1:
                            index = line.upper().find(f' {possible_ps} ')
                        if index == -1:
                            index = line.upper().find(f' {possible_ps}/')
                        if index != -1 and index < least_index:
                            print(f'Found: "{possible_ps}" at index "{index}" for "{line}"')
                            least_index = index
                    if least_index < 9999:
                        name = line[0:least_index]
                        status = line[least_index:]

                if re.search(r'/',status): #Finds / in status
                    if re.search(r'[()]',status): #Sees brackets, need to see if the / is in brackets
                        if status.find("/") > status.find(")") or status.find("/") < status.find("("): # )/ or /(
                            print("{}: Mix parade state".format(name))
                            try: #For )/
                                am_status = "{})".format(status.split(")/")[0])
                                pm_status = status.split(")/")[1]
                            except:
                                try: #For /...(
                                    am_status = status.split("/")[0]
                                    pm_status = "/".join(status.split("/")[1:])
                                except: #Give up, add to error_names
                                    error_names = "{}\n{}".format(error_names, line)
                                    continue
                            self.insert_ps(reg_am, reg_pm,name,am_status,pm_status)
                        else:
                            print("{}: Single parade state with date".format(name))
                            am_status = pm_status = status
                            self.insert_ps(reg_am, reg_pm,name,am_status,pm_status)
                        continue
                    else:
                        am_status = status.split("/")[0]
                        pm_status = "/".join(status.split("/")[1:])
                        self.insert_ps(reg_am, reg_pm,name,am_status,pm_status)
                        continue
                else: #Does not find / in status
                    if len(name) == 0:
                        name = line
                    if len(status) == 0:
                        status = "P"
                    am_status = pm_status = status
                    self.insert_ps(reg_am, reg_pm,name,am_status,pm_status)

            if line_no > absent: # Absent People
                if re.search(r' - ',line):
                    name = line.split(" - ")[0]
                    status = " - ".join(line.split(" - ")[1:])
                else:
                    least_index = 9999 #High number to start with
                    for possible_ps in common_ps:
                        index = line.upper().find(f' {possible_ps}')
                        if index + len(possible_ps) + 1 != len(line): #For those that end with the status. E.g. "XYZ VRS", else we will reject this (e.g. "Ah Haut VRS" detected status will be "H" instead of "VRS")
                            index = -1
                        if index == -1:
                            index = line.upper().find(f'-{possible_ps}')
                            if index + len(possible_ps) + 1 != len(line): #For those that end with the status. E.g. "XYZ VRS", else we will reject this (e.g. "Ah Haut VRS" detected status will be "H" instead of "VRS")
                                index = -1
                        if index == -1:
                            index = line.upper().find(f' {possible_ps} ')
                        if index == -1:
                            index = line.upper().find(f' {possible_ps}/')
                        if index != -1 and index < least_index:
                            print(f'Found: "{possible_ps}" at index "{index}" for "{line}"')
                            least_index = index
                    if least_index < 9999:
                        name = line[0:least_index]
                        status = line[least_index:]
                        if status[0] == "-":
                            status = status[1:]
                    else:
                        #BETA SUPPORT
                        await ctx.send("Could not detect parade state for `{}`, please enter the parade state manually: (e.g. `Tom - P/OS (Location)`) ```Format: (name) - (status)```".format(line))
                        try:
                            manps = await self.bot.wait_for('message', timeout=90, check=lambda message: message.author == ctx.author) #this will be raw text
                            manstatus = manps.content
                            name = manstatus.split(" - ")[0]
                            status = " - ".join(manstatus.split(" - ")[1:])
                        except asyncio.TimeoutError:
                            error_names = "{}\n{}".format(error_names, line)
                            continue
                if re.search(r'/',status): #Finds / in status
                    if re.search(r'[()]',status): #Sees brackets, need to see if the / is in brackets
                        if status.find("/") > status.find(")") or status.find("/") < status.find("("): # )/ or /(
                            try: #For )/
                                am_status = "{})".format(status.split(")/")[0])
                                pm_status = status.split(")/")[1]
                            except:
                                try: #For /...(
                                    am_status = status.split("/")[0]
                                    pm_status = "/".join(status.split("/")[1:])
                                except: #Give up, add to error_names
                                    error_names = "{}\n{}".format(error_names, line)
                                    continue
                            self.insert_ps(reg_am, reg_pm,name,am_status,pm_status)
                        else:
                            am_status = pm_status = status
                            self.insert_ps(reg_am, reg_pm,name,am_status,pm_status)
                        continue
                    else:
                        am_status = status.split("/")[0]
                        pm_status = "/".join(status.split("/")[1:])
                        self.insert_ps(reg_am, reg_pm,name,am_status,pm_status)
                        continue
                else: #Does not find / in status
                    am_status = pm_status = status
                    self.insert_ps(reg_am, reg_pm,name,am_status,pm_status)
                    continue
        #End Regular PS.
        #Start NSF PS.
        nsf_am = {}
        nsf_pm = {}
        nsf_lines = nsfps.content.split("\n")
        nsf_lines = [line for line in nsf_lines if len(line.strip())] #Remove lines with only whitespaces / newlines

        for line in nsf_lines:
            name = line.split(" - ")[0]
            status = " - ".join(line.split(" - ")[1:])
            if len(status) == 0 and re.search(r'[-]',line):
                #ALPHA
                least_index = 9999 #High number to start with
                for possible_ps in common_ps:
                    index = line.upper().find(f'-{possible_ps}')
                    if index + len(possible_ps) + 1 != len(line): #For those that end with the status. E.g. "X-YZ-P", else we will reject this (e.g. "Yan-Heng VRS" detected status will be "H" instead of "VRS")
                        index = -1
                    if index == -1:
                        index = line.upper().find(f'- {possible_ps}')
                        if index + len(possible_ps) + 2 != len(line): #For those that end with the status. E.g. "X-YZ-P", else we will reject this (e.g. "Yan-Heng VRS" detected status will be "H" instead of "VRS")
                            index = -1
                    if index == -1:
                        index = line.upper().find(f'-{possible_ps} ')
                    if index == -1:
                        index = line.upper().find(f'-{possible_ps}/')
                    if index == -1:
                        index = line.upper().find(f'- {possible_ps} ')
                    if index == -1:
                        index = line.upper().find(f'- {possible_ps}/')
                    if index != -1 and index < least_index:
                        print(f'Found: "{possible_ps}" at index "{index}" for "{line}"')
                        least_index = index
                if least_index < 9999:
                    name = line[0:least_index]
                    status = line[least_index+1:]
                    #BETA SUPPORT
                else:
                    await ctx.send("Could not detect parade state for `{}`, please enter the parade state manually: (e.g. `X-YZ - P/OS (ORD)`) ```Format: (name) - (status)```".format(line))
                    try:
                        manps = await self.bot.wait_for('message', timeout=90, check=lambda message: message.author == ctx.author) #this will be raw text
                        manstatus = manps.content
                        name = manstatus.split(" - ")[0]
                        status = " - ".join(manstatus.split(" - ")[1:])
                        if re.search(r'/',status): #Finds / in status
                            if re.search(r'[()]',status): #Sees brackets, need to see if the / is in brackets
                                if status.find("/") > status.find(")") or status.find("/") < status.find("("): # )/ or /(
                                    try: #For )/
                                        am_status = "{})".format(status.split(")/")[0])
                                        pm_status = status.split(")/")[1]
                                    except:
                                        try: #For /...(
                                            am_status = status.split("/")[0]
                                            pm_status = "/".join(status.split("/")[1:])
                                        except: #Give up, add to error_names
                                            error_names = "{}\n{}".format(error_names, line)
                                            continue
                                    self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                                else:
                                    am_status = pm_status = status
                                    self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                                continue
                            else:
                                am_status = status.split("/")[0]
                                pm_status = "/".join(status.split("/")[1:])
                                self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                                continue
                        else: #Does not find / in status
                            am_status = pm_status = status
                            self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                    except asyncio.TimeoutError:
                        error_names = "{}\n{}".format(error_names, line)
                        continue
                    continue
            elif len(status) == 0: #Those header lines...?
                continue
            print("Status: {}".format(status))
            if re.search(r'/',status): #Finds / in status
                if re.search(r'[()]',status): #Sees brackets, need to see if the / is in brackets
                    if status.find("/") > status.find(")") or status.find("/") < status.find("("): # )/ or /(
                        try: #For )/
                            am_status = "{})".format(status.split(")/")[0])
                            pm_status = status.split(")/")[1]
                        except:
                            try: #For /...(
                                am_status = status.split("/")[0]
                                pm_status = "/".join(status.split("/")[1:])
                            except: #Give up, add to error_names
                                error_names = "{}\n{}".format(error_names, line)
                                continue
                        self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                    else:
                        am_status = pm_status = status
                        self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                    continue
                else:
                    am_status = status.split("/")[0]
                    pm_status = "/".join(status.split("/")[1:])
                    self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                    continue

            else: #Does not find / in status
                am_status = pm_status = status
                self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                continue
        #End NSFs
        print(json.dumps(nsf_am, indent=2))
        print(json.dumps(nsf_pm, indent=2))
        print(json.dumps(reg_am, indent=2))
        print(json.dumps(reg_pm, indent=2))
        #Time to generate Parade State! Fml
        am_header = "{}\nAM Parade State for {}\n".format(self.unit, date)
        message_am = ""

        pm_header = "{}\nPM Parade State for {}\n".format(self.unit, date)
        message_pm = ""

        com_am = {}
        for status in reg_am:
            if status not in com_am:
                com_am[status] = {
                    "names": {}
                }
            for name in reg_am[status]["names"]:
                com_am[status]["names"][name] = reg_am[status]["names"][name]
            if status == "P" and debug != "debug":
                continue

        for status in nsf_am:
            if status not in com_am:
                com_am[status] = {
                    "names": {}
                }
            for n, name in enumerate(nsf_am[status]["names"], start=1):
                com_am[status]["names"][name] = nsf_am[status]["names"][name]

        for status in com_am:
            if status == "P" and debug != "debug": #Skip present people unless debug flag
                continue
            #Build for message
            status_list = ""
            for n, name in enumerate(com_am[status]["names"], start=1):
                #status_list += f"\n{name}{f' {com_am[status]["names"][name]}' if len(com_am[status]["names"][name]) else ''}"
                status_list += "\n{}. {}{}".format(n, name, f' {com_am[status]["names"][name]}' if len(com_am[status]["names"][name]) else '')
            #End build, append to message
            message_am += "\n\n*{}*: {}{}".format(status, len(com_am[status]["names"]), status_list)

        total = 0
        for status in nsf_am:
            total = total + len(nsf_am[status]["names"])
        for status in reg_am:
            total = total + len(reg_am[status]["names"])
        try:
            nsf_strength = len(nsf_am["P"]["names"])
        except:
            nsf_strength = 0
        try:
            reg_strength = len(reg_am["P"]["names"])
        except:
            reg_strength = 0
        current = nsf_strength + reg_strength
        nsf_total = 0
        for status in nsf_am:
            nsf_total = nsf_total + len(nsf_am[status]["names"])
        reg_total = 0
        for status in reg_am:
            reg_total = reg_total + len(reg_am[status]["names"])


        am_header = "{}Total Strength: {}\nCurrent Strength: {}\nNSF Strength: {}/{}\nRegular Strength (with PCs): {}/{}".format(am_header, total, current, nsf_strength, nsf_total, reg_strength, reg_total)
        await ctx.send("```AM Parade State```")
        if len(f'{am_header}\n{message_am}') < 2000:
            await ctx.send("{}{}".format(am_header, message_am))
        else: #Total message length is longer than Discord allowed, hence we're splitting it up.
            start_index = 0
            message2send = f'{am_header}{message_am}'
            while start_index < len(message2send):
                await ctx.send(message2send[start_index:start_index + 2000])
                start_index = start_index + 2000

        com_pm = {}
        for status in reg_pm:
            if status == "P" and debug != "debug":
                continue
            if status not in com_pm:
                com_pm[status] = {
                    "names": {}
                }
            for name in reg_pm[status]["names"]:
                com_pm[status]["names"][name] = reg_pm[status]["names"][name]

        for status in nsf_pm:
            if status not in com_pm:
                com_pm[status] = {
                    "names": {}
                }
            for n, name in enumerate(nsf_pm[status]["names"], start=1):
                com_pm[status]["names"][name] = nsf_pm[status]["names"][name]

        for status in com_pm:
            if status == "P" and debug != "debug": #Skip present people unless debug flag
                continue
            #Build for message
            status_list = ""
            for n, name in enumerate(com_pm[status]["names"], start=1):
                #status_list += f"\n{name}{f' {com_am[status]["names"][name]}' if len(com_am[status]["names"][name]) else ''}"
                status_list += "\n{}. {}{}".format(n, name, f' {com_pm[status]["names"][name]}' if len(com_pm[status]["names"][name]) else '')
            #End build, append to message
            message_pm += "\n\n*{}*: {}{}".format(status, len(com_pm[status]["names"]), status_list)

        total = 0
        for status in nsf_pm:
            total = total + len(nsf_pm[status]["names"])
        for status in reg_pm:
            total = total + len(reg_pm[status]["names"])
        try:
            nsf_strength = len(nsf_pm["P"]["names"])
        except:
            nsf_strength = 0
        try:
            reg_strength = len(reg_pm["P"]["names"])
        except:
            reg_strength = 0
        current = nsf_strength + reg_strength
        nsf_total = 0
        for status in nsf_pm:
            nsf_total = nsf_total + len(nsf_pm[status]["names"])
        reg_total = 0
        for status in reg_pm:
            reg_total = reg_total + len(reg_pm[status]["names"])


        pm_header = "{}Total Strength: {}\nCurrent Strength: {}\nNSF Strength: {}/{}\nRegular Strength (with PCs): {}/{}".format(pm_header, total, current, nsf_strength, nsf_total, reg_strength, reg_total)
        await ctx.send("```PM Parade State```")

        if len(f'{pm_header}\n{message_pm}') < 2000:
            await ctx.send("{}{}".format(pm_header, message_pm))
        else: #Total message length is longer than Discord allowed, hence we're splitting it up.
            start_index = 0
            message2send = f'{pm_header}{message_pm}'
            while start_index < len(message2send):
                await ctx.send(message2send[start_index:start_index + 2000])
                start_index = start_index + 2000

        if error_names != "These people are not added into the Parade State and the total count as I couldn't detect the state. Please manually insert these people into AM/PM parade state and edit the numbers:":
            await ctx.send(error_names)
        em = discord.Embed(title="Please remember to do the following before sending the Parade State in the WhatsApp group:", description='1) Make sure the total strength is correct\n2) Make sure the names are listed in descending Rank.', colour=0x00FF00)
        await ctx.send(embed=em)
        return

    @commands.command(brief='Prints NSF Parade State',name='nsf')
    async def nsf(self, ctx, debug = "false"):
        """
        Works the same as the cos command, but only with NSFs.
        """
        await ctx.send("Please send the NSF Parade State:")
        try:
            nsfps = await self.bot.wait_for('message', timeout=90, check=lambda message: message.author == ctx.author) #this will be raw text
        except asyncio.TimeoutError:
            await ctx.send("Command timeout.")
            return

        error_names = "These people are not added into the Parade State and the total count as I couldn't detect the state. Please manually insert these people into AM/PM parade state and edit the numbers:"

        #setup
        common_ps = "P|LL|UL|OL|CCL|UCCL|DUTY|VRS|D|GD|DR|AO|OS|RSI|RSO|MA|MC|HL|H|CSE|WFH|QO|OFF"
        common_ps = common_ps.split("|")

        #Start NSF PS.
        nsf_am = {}
        nsf_pm = {}
        nsf_lines = nsfps.content.split("\n")
        for line in nsf_lines:
            if re.search(r'^PS for [0-9]*/[0-9]*/[0-9]*',line):
                date = line[-8:]
                continue
            name = line.split(" - ")[0]
            status = " - ".join(line.split(" - ")[1:])
            if len(status) == 0 and re.search(r'[-]',line):
                #ALPHA
                least_index = 9999 #High number to start with
                for possible_ps in common_ps:
                    index = line.upper().find(f'-{possible_ps}')
                    if index + len(possible_ps) + 1 != len(line): #For those that end with the status. E.g. "X-YZ-P", else we will reject this (e.g. "Yan-Heng VRS" detected status will be "H" instead of "VRS")
                        index = -1
                    if index == -1:
                        index = line.upper().find(f'- {possible_ps}')
                        if index + len(possible_ps) + 2 != len(line): #For those that end with the status. E.g. "X-YZ-P", else we will reject this (e.g. "Yan-Heng VRS" detected status will be "H" instead of "VRS")
                            index = -1
                    if index == -1:
                        index = line.upper().find(f'-{possible_ps} ')
                    if index == -1:
                        index = line.upper().find(f'-{possible_ps}/')
                    if index == -1:
                        index = line.upper().find(f'- {possible_ps} ')
                    if index == -1:
                        index = line.upper().find(f'- {possible_ps}/')
                    if index != -1 and index < least_index:
                        print(f'Found: "{possible_ps}" at index "{index}" for "{line}"')
                        least_index = index
                if least_index < 9999:
                    name = line[0:least_index]
                    status = line[least_index+1:]
                    #BETA SUPPORT
                else:
                    await ctx.send("Could not detect parade state for `{}`, please enter the parade state manually: (e.g. `X-YZ - P/OS (ORD)`) ```Format: (name) - (status)```".format(line))
                    try:
                        manps = await self.bot.wait_for('message', timeout=90, check=lambda message: message.author == ctx.author) #this will be raw text
                        manstatus = manps.content
                        name = manstatus.split(" - ")[0]
                        status = " - ".join(manstatus.split(" - ")[1:])
                        if re.search(r'/',status): #Finds / in status
                            if re.search(r'[()]',status): #Sees brackets, need to see if the / is in brackets
                                if status.find("/") > status.find(")") or status.find("/") < status.find("("): # )/ or /(
                                    try: #For )/
                                        am_status = "{})".format(status.split(")/")[0])
                                        pm_status = status.split(")/")[1]
                                    except:
                                        try: #For /...(
                                            am_status = status.split("/")[0]
                                            pm_status = "/".join(status.split("/")[1:])
                                        except: #Give up, add to error_names
                                            error_names = "{}\n{}".format(error_names, line)
                                            continue
                                    self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                                else:
                                    am_status = pm_status = status
                                    self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                                continue
                            else:
                                am_status = status.split("/")[0]
                                pm_status = "/".join(status.split("/")[1:])
                                self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                                continue
                        else: #Does not find / in status
                            am_status = pm_status = status
                            self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                    except asyncio.TimeoutError:
                        error_names = "{}\n{}".format(error_names, line)
                        continue
                    continue
            elif len(status) == 0: #Those header lines...?
                continue
            print("Status: {}".format(status))
            if re.search(r'/',status): #Finds / in status
                if re.search(r'[()]',status): #Sees brackets, need to see if the / is in brackets
                    if status.find("/") > status.find(")") or status.find("/") < status.find("("): # )/ or /(
                        try: #For )/
                            am_status = "{})".format(status.split(")/")[0])
                            pm_status = status.split(")/")[1]
                        except:
                            try: #For /...(
                                am_status = status.split("/")[0]
                                pm_status = "/".join(status.split("/")[1:])
                            except: #Give up, add to error_names
                                error_names = "{}\n{}".format(error_names, line)
                                continue
                        self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                    else:
                        am_status = pm_status = status
                        self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                    continue
                else:
                    am_status = status.split("/")[0]
                    pm_status = "/".join(status.split("/")[1:])
                    self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                    continue

            else: #Does not find / in status
                am_status = pm_status = status
                self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                continue
        #End NSFs
        print(json.dumps(nsf_am, indent=2))
        print(json.dumps(nsf_pm, indent=2))
        #Time to generate Parade State! Fml
        am_header = "{}\nAM Parade State for {}\n".format(self.unit, date)
        message_am = ""

        for status in nsf_am:
            if status == "P" and debug != "debug":
                continue
            #Build for message
            status_list = ""
            for n, name in enumerate(nsf_am[status]["names"], start=1):
                #status_list += f"\n{name}{f' {com_am[status]["names"][name]}' if len(com_am[status]["names"][name]) else ''}"
                status_list += "\n{}{}".format(name, f' {nsf_am[status]["names"][name]}' if len(nsf_am[status]["names"][name]) else '')
            #End build, append to message
            message_am += "\n\n*{}*: {}{}".format(status, len(nsf_am[status]["names"]), status_list)

        total = 0
        for status in nsf_am:
            total = total + len(nsf_am[status]["names"])
        try:
            nsf_strength = len(nsf_am["P"]["names"])
        except:
            nsf_strength = 0
        current = nsf_strength
        nsf_total = 0
        for status in nsf_am:
            nsf_total = nsf_total + len(nsf_am[status]["names"])


        am_header = "{}Total Strength: {}\nCurrent Strength: {}\nNSF Strength: {}/{}".format(am_header, total, current, nsf_strength, nsf_total)
        await ctx.send("```AM Parade State```")
        if len(f'{am_header}\n{message_am}') < 2000:
            await ctx.send("{}{}".format(am_header, message_am))
        else: #Total message length is longer than Discord allowed, hence we're splitting it up.
            start_index = 0
            message2send = f'{am_header}{message_am}'
            while start_index < len(message2send):
                await ctx.send(message2send[start_index:start_index + 2000])
                start_index = start_index + 2000

        pm_header = "{}\nPM Parade State for {}\n".format(self.unit, date)
        message_pm = ""

        for status in nsf_pm:
            if status == "P" and debug != "debug":
                continue
            #Build for message
            status_list = ""
            for n, name in enumerate(nsf_pm[status]["names"], start=1):
                #status_list += f"\n{name}{f' {com_am[status]["names"][name]}' if len(com_am[status]["names"][name]) else ''}"
                status_list += "\n{}{}".format(name, f' {nsf_pm[status]["names"][name]}' if len(nsf_pm[status]["names"][name]) else '')
            #End build, append to message
            message_pm += "\n\n*{}*: {}{}".format(status, len(nsf_pm[status]["names"]), status_list)

        total = 0
        for status in nsf_pm:
            total = total + len(nsf_pm[status]["names"])
        try:
            nsf_strength = len(nsf_pm["P"]["names"])
        except:
            nsf_strength = 0
        current = nsf_strength
        nsf_total = 0
        for status in nsf_pm:
            nsf_total = nsf_total + len(nsf_pm[status]["names"])

        pm_header = "{}Total Strength: {}\nCurrent Strength: {}\nNSF Strength: {}/{}".format(pm_header, total, current, nsf_strength, nsf_total)
        await ctx.send("```PM Parade State```")

        if len(f'{pm_header}\n{message_pm}') < 2000:
            await ctx.send("{}{}".format(pm_header, message_pm))
        else: #Total message length is longer than Discord allowed, hence we're splitting it up.
            start_index = 0
            message2send = f'{pm_header}{message_pm}'
            while start_index < len(message2send):
                await ctx.send(message2send[start_index:start_index + 2000])
                start_index = start_index + 2000

        if error_names != "These people are not added into the Parade State and the total count as I couldn't detect the state. Please manually insert these people into AM/PM parade state and edit the numbers:":
            await ctx.send(error_names)
        em = discord.Embed(title="Please remember to do the following before sending the Parade State in the WhatsApp group:", description='1) Make sure the total strength is correct\n2) Make sure the names are listed in descending Rank.', colour=0x00FF00)
        await ctx.send(embed=em)
        return

    @commands.command(brief='Craft Cohorting Group parade states',name='ds')
    async def ds(self, ctx, debug = "false"):
        """
        For crafting parade states based on Cohorting Groups.
        """
        try:
            self.cohorts
        except:
            await ctx.reply(f"No cohorting groups found. Please set using `{config['GLOBAL_PREFIX']}setcohort`", mention_author=False)

        await ctx.reply("Please send the NSF Parade State:", mention_author=False)
        try:
            nsfps = await self.bot.wait_for('message', timeout=90, check=lambda message: message.author == ctx.author) #this will be raw text
        except asyncio.TimeoutError:
            await ctx.send("Command timeout.")
            return

        error_names = "These people are not added into the Parade State and the total count as I couldn't detect the state. Please manually insert these people into AM/PM parade state and edit the numbers:"

        #setup
        common_ps = "P|LL|UL|OL|CCL|UCCL|DUTY|VRS|D|GD|DR|AO|OS|RSI|RSO|MA|MC|HL|H|CSE|WFH|QO|OFF"
        common_ps = common_ps.split("|")
        namelist = set()

        #Start NSF PS.
        nsf_am = {}
        nsf_pm = {}
        nsf_lines = nsfps.content.split("\n")
        for line in nsf_lines:
            if re.search(r'^PS for [0-9]*/[0-9]*/[0-9]*',line):
                date = line[-8:]
                continue
            name = line.split(" - ")[0]
            status = " - ".join(line.split(" - ")[1:])
            if len(status) == 0 and re.search(r'[-]',line):
                #ALPHA
                least_index = 9999 #High number to start with
                for possible_ps in common_ps:
                    index = line.upper().find(f'-{possible_ps}')
                    if index + len(possible_ps) + 1 != len(line): #For those that end with the status. E.g. "X-YZ-P", else we will reject this (e.g. "Yan-Heng VRS" detected status will be "H" instead of "VRS")
                        index = -1
                    if index == -1:
                        index = line.upper().find(f'- {possible_ps}')
                        if index + len(possible_ps) + 2 != len(line): #For those that end with the status. E.g. "X-YZ-P", else we will reject this (e.g. "Yan-Heng VRS" detected status will be "H" instead of "VRS")
                            index = -1
                    if index == -1:
                        index = line.upper().find(f'-{possible_ps} ')
                    if index == -1:
                        index = line.upper().find(f'-{possible_ps}/')
                    if index == -1:
                        index = line.upper().find(f'- {possible_ps} ')
                    if index == -1:
                        index = line.upper().find(f'- {possible_ps}/')
                    if index != -1 and index < least_index:
                        print(f'Found: "{possible_ps}" at index "{index}" for "{line}"')
                        least_index = index
                if least_index < 9999:
                    name = line[0:least_index]
                    status = line[least_index+1:]
                    #BETA SUPPORT
                else:
                    await ctx.send("Could not detect parade state for `{}`, please enter the parade state manually: (e.g. `X-YZ - P/OS (ORD)`) ```Format: (name) - (status)```".format(line))
                    try:
                        manps = await self.bot.wait_for('message', timeout=90, check=lambda message: message.author == ctx.author) #this will be raw text
                        manstatus = manps.content
                        name = manstatus.split(" - ")[0]
                        status = " - ".join(manstatus.split(" - ")[1:])
                        if re.search(r'/',status): #Finds / in status
                            if re.search(r'[()]',status): #Sees brackets, need to see if the / is in brackets
                                if status.find("/") > status.find(")") or status.find("/") < status.find("("): # )/ or /(
                                    try: #For )/
                                        am_status = "{})".format(status.split(")/")[0])
                                        pm_status = status.split(")/")[1]
                                    except:
                                        try: #For /...(
                                            am_status = status.split("/")[0]
                                            pm_status = "/".join(status.split("/")[1:])
                                        except: #Give up, add to error_names
                                            error_names = "{}\n{}".format(error_names, line)
                                            continue
                                    self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                                else:
                                    am_status = pm_status = status
                                    self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                                continue
                            else:
                                am_status = status.split("/")[0]
                                pm_status = "/".join(status.split("/")[1:])
                                self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                                continue
                        else: #Does not find / in status
                            am_status = pm_status = status
                            self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                    except asyncio.TimeoutError:
                        error_names = "{}\n{}".format(error_names, line)
                        continue
                    continue
            elif len(status) == 0: #Those header lines...?
                continue

            namelist.add(name.strip().lower()) #We add to the total NR so we can compare later on

            print("Status: {}".format(status))
            if re.search(r'/',status): #Finds / in status
                if re.search(r'[()]',status): #Sees brackets, need to see if the / is in brackets
                    if status.find("/") > status.find(")") or status.find("/") < status.find("("): # )/ or /(
                        try: #For )/
                            am_status = "{})".format(status.split(")/")[0])
                            pm_status = status.split(")/")[1]
                        except:
                            try: #For /...(
                                am_status = status.split("/")[0]
                                pm_status = "/".join(status.split("/")[1:])
                            except: #Give up, add to error_names
                                error_names = "{}\n{}".format(error_names, line)
                                continue
                        self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                    else:
                        am_status = pm_status = status
                        self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                    continue
                else:
                    am_status = status.split("/")[0]
                    pm_status = "/".join(status.split("/")[1:])
                    self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                    continue

            else: #Does not find / in status
                am_status = pm_status = status
                self.insert_ps(nsf_am, nsf_pm,name,am_status,pm_status)
                continue
        #End NSFs
        print(json.dumps(nsf_am, indent=2))
        print(json.dumps(nsf_pm, indent=2))

        #Time to generate Parade State!
        cohort_msg_am = f'{self.unit} AM Strength {date}'
        cohort_msg_pm = f'{self.unit} PM Strength {date}'

        to_check_namelist = set()
        for cohort in self.cohorts:

            cohort_amheader = cohort_pmheader = "*Cohort: {}*\n".format(cohort)
            cohort_am = {}
            for status in nsf_am:
                if status not in cohort_am:
                    cohort_am[status] = {
                        "names": {}
                    }
                for name in nsf_am[status]["names"]:
                    if name.strip().lower() in self.cohorts[cohort]:
                        print(f'{cohort}: {name}')
                        cohort_am[status]["names"][name] = nsf_am[status]["names"][name]
                        to_check_namelist.add(name.strip().lower()) #Add to the comparing namelist
                if len(cohort_am[status]["names"]) == 0:
                    del cohort_am[status]
            message_amcohort = ""
            for status in cohort_am:
                #Build for message
                status_list = ""
                for n, name in enumerate(cohort_am[status]["names"], start=1):
                    #status_list += f"\n{name}{f' {com_am[status]["names"][name]}' if len(com_am[status]["names"][name]) else ''}"
                    status_list += "\n{}. {}{}".format(n, name, f' {cohort_am[status]["names"][name]}' if len(cohort_am[status]["names"][name]) else '')
                #End build, append to message
                message_amcohort += "\n\n_{}_: {}{}".format(status, len(cohort_am[status]["names"]), status_list)


            total = 0
            for status in cohort_am:
                total = total + len(cohort_am[status]["names"])
            try:
                nsf_strength = len(cohort_am["P"]["names"])
            except:
                nsf_strength = 0

            cohort_amheader = "{}NSF Strength: {}/{}".format(cohort_amheader, nsf_strength, total)
            #await ctx.send(f"```AM Parade State (Cohort {cohort})```")

            cohort_msg_am += "\n\n=========\n\n{}{}".format(cohort_amheader, message_amcohort)

            #if len(f'{cohort_amheader}{message_amcohort}') < 2000:
            #    await ctx.send("{}{}".format(cohort_amheader, message_amcohort))
            #else: #Total message length is longer than Discord allowed, hence we're splitting it up.
            #    start_index = 0
            #    message2send = f'{cohort_amheader}{message_amcohort}'
            #    while start_index < len(message2send):
            #        await ctx.send(message2send[start_index:start_index + 2000])
            #        start_index = start_index + 2000

            cohort_pm = {}
            for status in nsf_pm:
                if status not in cohort_pm:
                    cohort_pm[status] = {
                        "names": {}
                    }
                for name in nsf_pm[status]["names"]:
                    if name.strip().lower() in self.cohorts[cohort]:
                        cohort_pm[status]["names"][name] = nsf_pm[status]["names"][name]
                if len(cohort_pm[status]["names"]) == 0:
                    del cohort_pm[status]

            message_pmcohort = ""
            for status in cohort_pm:
                #Build for message
                status_list = ""
                for n, name in enumerate(cohort_pm[status]["names"], start=1):
                    #status_list += f"\n{name}{f' {com_am[status]["names"][name]}' if len(com_am[status]["names"][name]) else ''}"
                    status_list += "\n{}. {}{}".format(n, name, f' {cohort_pm[status]["names"][name]}' if len(cohort_pm[status]["names"][name]) else '')
                #End build, append to message
                message_pmcohort += "\n\n_{}_: {}{}".format(status, len(cohort_pm[status]["names"]), status_list)

            total = 0
            for status in cohort_pm:
                total = total + len(cohort_pm[status]["names"])
            try:
                nsf_strength = len(cohort_pm["P"]["names"])
            except:
                nsf_strength = 0

            cohort_pmheader = "{}NSF Strength: {}/{}".format(cohort_pmheader, nsf_strength, total)
            #await ctx.send(f"```PM Parade State (Cohort {cohort})```")

            cohort_msg_pm += "\n\n=========\n\n{}{}".format(cohort_pmheader, message_pmcohort)

            #if len(f'{cohort_pmheader}{message_pmcohort}') < 2000:
            #    await ctx.send("{}{}".format(cohort_pmheader, message_pmcohort))
            #else: #Total message length is longer than Discord allowed, hence we're splitting it up.
            #    start_index = 0
            #    message2send = f'{cohort_pmheader}{message_pmcohort}'
            #    while start_index < len(message2send):
            #        await ctx.send(message2send[start_index:start_index + 2000])
            #        start_index = start_index + 2000

        await ctx.send(f"```AM Cohort Groups Parade State```")
        if len(cohort_msg_am) < 2000:
            await ctx.send(cohort_msg_am[10:])
        else: #Total message length is longer than Discord allowed, hence we're splitting it up.
            start_index = 10
            message2send = cohort_msg_am
            while start_index < len(message2send):
                await ctx.send(message2send[start_index:start_index + 2000])
                start_index = start_index + 2000

        await ctx.send(f"```PM Cohort Groups Parade State```")
        if len(cohort_msg_pm) < 2000:
            await ctx.send(cohort_msg_pm[10:])
        else: #Total message length is longer than Discord allowed, hence we're splitting it up.
            start_index = 10
            message2send = cohort_msg_pm
            while start_index < len(message2send):
                await ctx.send(message2send[start_index:start_index + 2000])
                start_index = start_index + 2000

        if error_names != "These people are not added into the Parade State and the total count as I couldn't detect the state. Please manually insert these people into AM/PM parade state and edit the numbers:":
            await ctx.send(error_names)

        not_added = namelist - to_check_namelist
        if len(not_added):
            error_names = discord.Embed(title="These people are not detected as part of any cohort, and are not included in **any** cohort group parade states. Please manually insert these people into AM/PM parade state and edit the numbers:", description="\n".join([f'{n}. {name.title()}' for n, name in enumerate(not_added, start=1)]), colour = 0xff0000)
            if error_names != "These people are not detected as part of any cohort, and are not included in **any** cohort group parade states. Please manually insert these people into AM/PM parade state and edit the numbers:":
                await ctx.send(embed=error_names)
        em = discord.Embed(title="Please remember to do the following before sending the Parade State in the WhatsApp group:", description='1) Make sure the total strength is correct\n2) Make sure the names are listed in descending Rank.', colour=0x00FF00)
        await ctx.send(embed=em)
        return

def setup(bot):
    bot.add_cog(PS(bot))
