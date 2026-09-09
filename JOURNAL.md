I copy pasted all these journals from macondo so sorry for shitty layout

## Humble Beginnings
6 Jul 2026, 22:25

Welcome, this is the start of my calculator. So far, I only implemented the most basic way of calculating the position of a Minecraft stronghold, which involves taking the angle of the Eye of Ender at 2 different positions and then intersecting the lines they make. It's pretty basic, but it is a start and gets something working at least.

Next, I am going to add a way to notify the user of incorrect measurements utilising stronghold spawning and snapping mechanics, but I won't go into detail about that just yet, as I want to explain it well. Attached below are the results of the calculator. As you can see, they are quite accurate, and the tiny mismatch will be caught by snapping mechanics; however, due to my calculator drawing an infinitely thin line. It often needs to do 2 sets of measurements if you are trying to find something from more than like, 500 blocks away. In this example, we were only like 350 blocks away, so it was really accurate.

![image](https://cdn.hackclub.com/019f394e-b95e-7860-90c5-4c63c8746d2c/image.png)

![image](https://cdn.hackclub.com/019f394e-e567-7de2-852c-b0d3942ea29c/image.png)

## Some small QOL
7 Jul 2026, 17:41

I added a few small improvements to the triangulation such as displaying the corresponding nether coordinates as to where the stronghold is predicted to be as well as some small code to snap the calculated position to 8, 8 of the chunk (which is where the eye points to). The final small improvement was to add in the reigons where all the strongholds lie so users can more easily identify if the coordinates provided are reasonable or not. image
![image](https://cdn.hackclub.com/019f3d74-4b7f-7d48-921f-ea496b3eba88/image.png)

The next improvement will be to learn this math to be able to implement it into the calculator to be able to tell the user how reliable their prediction is utilising the triangular way strongholds generate.image
![image](https://cdn.hackclub.com/019f3d76-e51d-7edf-be61-b8c24e2e572e/image.png)

## Math is scary. But I overcame it + optimisations!
20 Jul 2026, 21:29

So it's been a while since last time, to say the least. And I have rewritten this journal a few times since, so the actual date of this journal is 31/07/2026.

So what have I actually been up to all this time? Well, I have been working on creating the statistical model for the calculator.

I alr explained how it works in my README, so I am not going to explain it again here. But I do want to mention some of the issues I ran into whilst trying to make this, which caused such a large amount of hours.

Firstly, I actually tried to understand what the fuck was going on. The paper has a lot of variables and letters that it created to define stuff. Half of which is not properly explained before using it in the equations. Quite a bit, which also is not explained really, and I needed to figure out what it was actually doing. So I figured it out then, after MANY HOURS. I finally get it in a functioning state, I think. At first, I thought oh this works and i didnt even need to implement the really fancy maths. But guess what. My implementation was ONLY CORRECT FOR THE FIRST RING.

So I had to go implement the fancy double integral math, which took a while, then eventually I got it working, but there was one itsy bitsy issue. It was WAYYYYYYYYY too slow. So I had to find some ways to cut corners. I did this in a few ways.

First, I reduced the search scope from every ring to only the ones where the eye could be pointing, which reduces the scope from 8 rings down to like 3 maximum. Then, I vectorised a bunch of the code, which was using slow ass python for loops to cool numpy vector calcs. But this STILL was not fast enough.

Then I discovered a bug where I was actually deleting the best candidates for where the stronghold was as I was finding them, which means as you're using it, the calculator kept getting less accurate. So I had to fix that.

Then the biggest optimisation came with changing the way I computed the integral. Before, I would accurately compute the integral by actually doing it. I changed it to be a Simpson integral approximation, which massively improved performance times, as I could instead create an accurate estimate, which is MUCH faster to do and loses negligable amounts of accuracy.

Afterwards, I added 2 more optimisations. Both of which revolved around reducing the scope we are analysing. Before, we were still analysing large amounts of data. Sure, we cut it down from 8 rings to 3, but even then, we are analysing massive amounts of data. And whilst the Simpson integral is fast, it still takes longer than I would like to complete. So my final trick was MURDER! Yay! What we are pretty much doing here is pruning everything which is not within a certain size angle of the measurement, then doing some math on the weights. Then we are also pruning all the positions which have no chance of being the correct position ever.

Only after all that do we pass in the surviving candidates into the integral, which moves the amount of chunks processed from like 100s of thousands to only 100s if that.

## GUI GUI GUI (I dont like gui) + Angle locking!
4 Aug 2026, 22:57
So I am making a really basic GUI which is enough for users to use the program reasonably. I am not doing more as I HATE GUI FUCK GUI IT IS JUST NOT FUN. Sooo this is what the gui looks like. image

![image](https://cdn.hackclub.com/019fcec1-30b9-7b5c-b1b9-688bf2b79410/image.png)

Yes i know it looks ugly as shit. No, I will not be improving it fuck you.

So let me go on to the other new feature I implemented. Angle locking. So let's say you found the stronghold :yay:. Now you want to actually get there, and as your traveling, you are getting a bit off course. So, how do you check how off course you are? What if instead you could just take a measurement of your current position and be told how far u are from the target coordinates and what the new angle you should be travelling in is?

Pretty nifty, aye? So I added that, and now if you lock your position, you every time you press f3+c whilst locked, you instead update the distance and angle numbers, which tell you the new distance and angle you need to travel to get to your destination. Along with this i also implemented a little arrow indicator telling you the direction you need to turn and by how much. Very convenient when u end up off angle due to funky nether terrain.

## Seedsearching Failures in Java
6 Aug 2026, 16:30

So I decided to feature creep my project and add a seed filter. The idea behind it is simple. Playing Bad Seeds is not fun at all. So what if instead you could only play the good ones? Like the ones where all the structures you want are nearby, you spawn with a completable ruined portal and all the iron you want so you can get a sub-2-minute Nether enter. That would be fun!

So I wanted to implement just that. I found a seed-finding tutorial that was really well-made from Kris, so I learned some of the basics I needed from there and started making my own filter to search for a good ruined portal seed. I was able to get the loot and searching stuff figured out after a while, and was making solid progress.

However, I quickly ran into one problem. Ruined portals are ANNOYING AS FUCK. Why are you wondering? Well, it turns out that ruined portals LOVE spawning underground. Ok, that should not be hard to deal with. Just check if it spawns above ground, silly. Well, it turns out Minecraft gives NO indication as to what the Y level it will spawn at. This is as much info as I can get. image

![image](https://cdn.hackclub.com/019fd7bb-6afb-7a41-91a8-14196a5222d8/image.png)

So my next idea was, hey, why don't I just try to find out what the block is that is spawning at the ground level of that position in the world? It should not be too hard, as logically we should find something like netherack or another unnatural thing on that block. Turns out the libary I am using is shit and only thinks the game has 3 blocks, water, stone and air. Thanks, game. Really useful. image

![image](https://cdn.hackclub.com/019fd7c4-aceb-7ca2-9958-9925021f9f30/image.png)

So I cannot currently think of another way of checking the best way to check if a ruined portal is above the surface. If u think of one please lmk.

## The filter is complete! (Well as much as I care to complete it)
14 Aug 2026, 17:07

So I completely gave up on solving the ruined portal issue. I instead decided to focus my efforts on the other 4 relevant overworld structures for a Minecraft speedrun. Those being a Shipwreck, Village, Desert Temple and Buried Treasure.

Before we go into the specific details of each seed type, let's first clarify some details. Firstly, what do we actually want out of each seed? Well, in our case, we want to be able to craft the following.

    Iron Pickaxe or better
    Bucket
    Some source of fire

The pickaxe is to mine gold blocks for piglin bartering (more on this later).
The bucket is so we can make a Nether portal, as that is the next major part of the speedrun.
We also need a source of fire. In the case of a ruined portal, this can be a Fire Charge; however, most structures won't contain this, so we can provide the player with 1 extra iron, and they can craft a flint and steel.

Furthermore, we also want this structure to be reasonably close to us. Anywhere like < 6 or so chunks away. (96 blocks) is fairly reasonable, as the structures are often quite big. However, we also don't want to be too restrictive, as otherwise finding valid seeds can take much longer.

Next we have the bastion. This is also a fundamental part of the speedrun, as it allows us to gather many of the required resources for killing the Ender Dragon, such as Ender Pearls, blocks, string, etc. Therefore, whenever we find a valid seed, we also want to search that seed for whether it has any bastions close by. There are 4 types of bastions, but all of them have different routes devised for them that most speedrunners know, so there is no filtering by bastion type as of right now.

Now that we have devised the general criteria needed, we can start exploring the different issues and experiences with filtering each seed type.
### Desert Temple

So this one is fairly simple. What you want is a seed where you can guarantee the player at least 7 iron or 4 iron and 3 diamonds. This seed type is very fast and easy to filter for. No issues here; perfect score here. Nice, simple, easy to do and very time-efficient. No issues with finding it here, as they try to spawn above ground and pretty much always will do so.
### Buried Treasure

This one is also very simple. No very costly searches needed here. Pretty much the same requirements here. But the main thing is the player needs to be good at identifying buried treasures, as they never spawn surface-exposed. In a speedrun, you would need to use the pie chart to identify one.
### Shipwreck

This one should theoretically not be very intensive, as you are computing pretty much the same thing as the other ones; however, for some reason, in testing, these seeds took SIGNIFICANTLY longer to search for, and I am honestly not sure why.
### Villages

This one takes a bit long, but there is a valid reason for it. Because of the way villages are generated, they are many smaller structures put together in a jigsaw to make the larger set (the full village). What makes this worse is that this is unique to each sister seed. (Minecraft seeds are 64-bit. Some parts use only the first 48 bits; some use the whole 64 bits. So the parts which use the first 48 bits can be computed once before checking all the sister seeds (65536 sisters)). With villages, they rely on the full 64-bit seed for pretty much all their generation, so a lot more work needs to be done per seed compared to other structures.

Now that we have figured out how that is going to work, we also need to filter for bastions. Those must be complicated, right? Guess what. They are easy as hell. Because you don't care what is in the chests, you only want to make sure that there is a nearby bastion; it ends up being trivial to filter for.

Some of you may be wondering, Hey, don't we need to also filter for some way for the player to be able to enter the Nether, like a nearby lava pool or magma ravine? Well turns out that is wayyyy too annoying, so I cannot be asked to do that.

Whilst we are on that topic, should we not be filtering for nearby fortresses too? Well, we should, but I genuinely cannot be asked to, so we are not.

Now, onto the various issues I ran into when developing this, to justify why I have spent so much time on this part. Firstly, the libraries I am using have next-to-nonexistent documentation written for them. So I have been relying on this one YouTube video series and reading source code to find what I am looking for.

Furthermore, I have been trying to optimise this code a bit so it can run faster and search for good seeds more quickly. However, small issue: I know jack shit about Java, so I am figuring out a lot of things for the first time. So that is funnnn. So all in all, pwetty pwese don't deflate me.

## Standard Deviation Configuration!
19 Aug 2026, 00:11

So, the final journal: what a journey it has been. Anyway, what did I do THIS time? Well, I worked on a way for the user to actually configure the standard deviation. This is the only bit of setup the user has to do, and it is critically important to how accurate the calculator is. I am too tired to explain what the standard deviation does exactly, so just know it lets us know how much we should trust the user's measurements.

So the actual difficult part was not figuring out how to be able to measure how accurate people were with their measurements. That was fairly easy. What you do is ask the user to enter the coordinates of the closest stronghold. Then you can just ask them to measure the eye as they normally would in a speedrun. After each measurement, you then move them around a bit and ask them to measure again. Repeat this until you have a value which has settled, and you can use this to calculate the standard deviation.

Now, what was the difficult part? GUI GUI GUI I HATE GUI. So getting the GUI to properly coordinate with what I wanted to do was fun. Firstly, I needed to find out how to delete old GUI elements. Not that bad; I found a Stack Overflow thread that helped me there.

Next, my major issue was that it would keep freezing up whenever I would try to send in an F3+C position. So I eventually realised it was because I had 2 threads running at the same time, both of which were requesting F3+C information (the main calculator and the standard deviation configurer). There was also another issue where the threads listening for the F3+C input would end up blocking the program from closing properly. So I had to add a fix for that.

I also added a way for people to manually enter their standard deviation value if they already know it. That is pretty much it. Thank you for joining me on this journey im eepy so im off to bed. Nighty :3
