import discord, dotenv, os

intents = discord.Intents.default()
intents.message_content = True

dotenv.load_dotenv()
token = str(os.getenv("TOKEN"))

client = discord.Client(intents=intents)
bot = discord.Bot()

f = open("course_list.txt", "r+")
course_list = f.readlines()
for i in range(len(course_list)):
    course_list[i] = course_list[i].strip()

course = bot.create_group("course", "Course-related commands")
study_path = bot.create_group("study_path", "Study path planning commands")

def find_role(name: str, role_list: list[discord.Role]) -> discord.Role:
    for r in role_list:
        if r.name == name.lower():
            return r

@course.command(name = "join", description = "Join an existing course channel")
async def join_course(ctx: discord.Interaction, name: str):
    await ctx.response.defer()
    try:
        if len(name) != 8:
            await ctx.respond(f"Error: name is invalid!")
            return
        for c in name[:4]:
            if not c.isalpha():
                await ctx.respond(f"Error: name is invalid")
                return
        for c in name[4:]:
            if not c.isnumeric():
                await ctx.respond(f"Error: name is invalid")
                return
        formatted_name = name.upper()
        server = ctx.guild
        role_list = server.roles
        role = find_role(name.lower(), role_list)
        await ctx.user.add_roles(role)
        await ctx.followup.send(f"Joined {formatted_name}'s channel.")
    except Exception as e:
        await ctx.followup.send("An error has occurred. Please try again!")
        print(e)

@course.command(name = "create", description = "Create a new course channel")
async def create_course(ctx: discord.Interaction, name: str):
    await ctx.response.defer()
    try:
        if len(name) != 8:
            await ctx.respond(f"Error: name is invalid!")
            return
        for c in name[:4]:
            if not c.isalpha():
                await ctx.respond(f"Error: name is invalid!")
                return
        for c in name[4:]:
            if not c.isnumeric():
                await ctx.respond(f"Error: name is invalid!")
                return
        if name.lower() in course_list:
            await ctx.respond(f"Error: channel already exists!")
            return
        channel_name = name[:4].lower() + "-" + name[4:]
        formatted_name = name.upper()
        server = ctx.guild
        role_list = server.roles
        role_names = [r.name for r in role_list]
        role = None
        if name.lower() not in role_names:
            role = await server.create_role(name=name.lower(), mentionable=True)
        else:
            role = find_role(name.lower(), role_list)
        category_list = server.categories
        category = None
        category_name = str(os.getenv("CATEGORY_NAME"))
        for c in category_list:
            if c.name == category_name:
                category = c
                break
        if category != None:
            channel = await server.create_text_channel(name=channel_name, category=category)
            for r in role_list:
                await channel.set_permissions(target=r, overwrite=discord.PermissionOverwrite(view_channel=False))
            await channel.set_permissions(target=role, overwrite=discord.PermissionOverwrite(view_channel=True))
            if name.lower() not in course_list:
                f.write(name.lower() + '\n')
                course_list.append(name.lower())
                course_list.sort()
        await ctx.followup.send(f"Created channel for {formatted_name}.")
    except Exception as e:
        await ctx.followup.send("An error has occurred. Please try again!")
        print(e)

@course.command(name = "list", description = "List currently existing course channels")
async def list_course(ctx: discord.Interaction):
    await ctx.response.defer()
    msg = "List of course channels:\n"
    for i in sorted(course_list):
        msg += '* ' + i.upper() + '\n'
    msg.strip()
    await ctx.followup.send(msg)

@study_path.command(name = "req", description = "List a major's requirements")
async def major_req(ctx: discord.Interaction, name: str):
    await ctx.response.defer()
    msg = f"{name.upper()}'s major requirements:\n"
    await ctx.followup.send(msg)

@client.event
async def on_ready():
    print("bot is now online")

bot.run(token)