# StupidBrain

A Minecraft stronghold calculator which utilises a bayesian statistics method of calculating the position of the stronghold. This approach implements the methods layed out in [this document](RMassets/triangulation.pdf) made by the very smart and cool NingaBrain. This entire bot is my attempt at recreating [his bot](https://github.com/Ninjabrain1/Ninjabrain-Bot) myself out of curiosity.

---

## Usage guide

I have prepared a video as shown below to showcase how to use this calculator properly in order to set it up so you can begin measuring eyes. 

[WILL BE ADDED LATER]

You will first need to configure a standard deviation. This will be how accurate your measurements are to the actual angle the eye is pointing. This is a value you will give in degrees. A good starting off value if you are casually playing is 0.1 as it will require you to measure somewhat accurately but is fairly lenient. And should give you a decent prediction.

To measure the eye, I reccomend you lower FOV to 30 and your sensitivity to 0/\*yawn* one your crosshair is on the eye for better measurement. As you can see below you want the right edge of your crosshair to align with the left side of the centre pixel of the eye. This is the optimal measurement. If you are unable to get this accurate, it is OK, but a better accuracy will lead to much more accurate measurements. ![img.png](RMassets/eyealign.png)

Once aligned press the combination of "F3" + "C" with the game unpaused. This will copy position data about your minecraft player which the program will then read and update its prediction. 

---
## How does this work

If you want a good explanation without going over the exact math behind this calculator I highly reccomend checking out [this video](https://www.youtube.com/watch?v=jZ8fh-LJB88) by Heppe as well as [this video](https://www.youtube.com/watch?v=rglAku0nrKM&t=355s) by DIMM4; both of which significantly helped me as well in understand what the idea and logic behind the bot was.

### An Overview of the Logic

If you are too lazy to watch those videos and just want me to explain it read this section.  

#### The Stupid Method
In Minecraft you have an Eye of Ender. What this item does is point to the closest stronghold in the world from your current position. If you are playing casually you would look at the direction the eye is going and then walk in that direction until you felt you went far enough then throw another eye. This method is horrible and ineffienct. It gives you no sense of distance you need to travel and you can easily overshoot the stronghold (The circles are the eyes of ender).  
![badmethod.png](RMassets/badmethod.png)
So let's improve this.  

#### The Mediocre Method
Now what if instead we upgraded to throwing 2 eyes. What we could do is measure the angle the eye is pointing at 2 different positions and note down the angle the eye was pointing in as well as the X and Z coordinates of each place we measured. This would allow us to form 2 lines and intersect them. We can then apply basic triginometry to be able to tell where the lines are intersecting.

![betterbutstillbadmethod.png](RMassets/betterbutstillbadmethod.png)

This should be where the stronghold is right? Theoretically, yes. But in reality this is not the case. Often, when you try this you are still 100's of blocks away from the stronghold which is miniutes of time loss in a speedrun. Now why is that? 

1. Humans are not accurate. We are not able to consistently measure accurately enough to get a goof. 
2. Minecraft only gives us the angle you are facing to 2 decimal places. This can cause lots of inaccuracy over the distance of 1000's of blocks leading to incorrect answers. 

So let's improve this.

#### The Pro Method
So after all that waffle here is what this method does different. It has 2 different parts which combine together to create the full bot. 

The first part is where we create a set of every possible coordinate where the stronghold could be pointing to. You may think that this is near infinte however we can do quite a few things to eliminate this. Down to something more reasonable. Firstly strongholds can only spawn in the set reigons shown in the image below.
![img.png](RMassets/reigons.png)

Secondly, each stronghold must start generating at the 8, 8 coordinate in a chunk (a chunk is 16x16 blocks large). With this we can create a large but managable list of every possible coordinate a stronghold can point to. A bit like this.
![img.png](RMassets/setofcoords.png)

Now we have this large set we can measure angle the eye is pointing as well as where the player is standing. With this info we can calculate what are the chances these coordinates were the actual ones the eye of ender was pointing to. This diagram below shows a cone/triangleish shape which is a range of possible angles your eye of ender could be pointing to. 
![img.png](RMassets/coneangle.png)

Now why are we forming this shape? Well that is because of the main issue which the previous method did not address. Inaccuracy with measurements. We can resolve this by normally distributing the measured angle with a standard deviation being the angle in degrees that the player's measurements vary by. What this essentially means is that we are 

Then we can combine all this together to create a list of probable candidates where the stronghold could be. 

### The Math behind it

The paper starts off by algebraically defining the locations of a stronghold within a ring (let's call this ring k).  
![strongholdinitplacement.png](RMassets/strongholdinitplacementfull.png)

We are first randomly generating and angle between 0 and 2π (aka 0 and 360 degrees but for ease we will be using radians for the rest of the explanation).  
![randangleoffset.png](RMassets/randangleoffset.png)

Then we are equally distributing this across the entire ring lets say the ring had 3 strongholds n_k would be 3 and the variable "i" would increment from 0 to 2. This results in the strongholds being equal angles apart  
![placeangle.png](RMassets/placeangle.png)

This randomly decides how far away from (0, 0) the strongholds should be placed using a uniform distribution (all numbers have equal chance). a_k and b_k are the start and end displacements of the ring reigons.  
![randdisplace.png](RMassets/randdisplace.png)

Afterwards, the stronghold does 2 different snaps. One to the 8,8 coordinate of the chunk. Another, will be a biome snap where it tries to search for a valid place to place the stronghold anywhere between 0 and 128√2 blocks in any direction.  
![snapoffset.png](RMassets/snapoffset.png)

Now we know how the strongholds are placed, I want to jump a bit ahead to how the measurement error is accounted for becuase it makes a lot more sense chronologically. The measurement error essentially deciding how accurate is your measurement and how much should it be trusted.

That's why we add in some extra math to account for the errors we get with both Minecraft and human imprecision.

This first line here basically means we are going to create a massive set with every possible coordinate the eye could be pointing to. This is possible because there are a pretty finite amount of places where one can spawn. Only (8, 8) coordinates in a chunk which is in one of the ring reigons. 
![g_set_init.png](RMassets/g_set_init.png)  

When we read the player's measurement of the eye of ender angle we assume it is [normally distributed](https://en.wikipedia.org/wiki/Normal_distribution) with the standard deviation being a value they themselves select. The standard deviation should be how much the player's measurements vary by when they measure the eye. The mean for the distribution is 0 (a perfect measurement). This is because a player's measurements should vary equal amounts to the left and right. The normal distriubtion is calculated as a [PDF](https://en.wikipedia.org/wiki/Probability_density_function) We add this to the theoretically perfect angle between you and the stronghold. This math is then repeated for every throw as well as for each chunk in the set G. Then we apply [Bayes' Theroem](https://en.wikipedia.org/wiki/Bayes%27_theorem) to update our probabilites as more eyes are thrown.   
![measurementerror.png](RMassets/measurementerror.png)

Now we can go back to finding the closest stronghold. This is mostly where all the scary parts come into play. I won't go into exact detail with this as I am yet to fully understand it myself but the general idea here is we are each comparing each candidate chunk (i in this case) to each other one (l) and trying to find what are the chances there is a closer stronghold. R1 and R0 are the bounds where if a l spawns inside it is closer to you than i.   
![candidatecloser.png](RMassets/candidatecloser.png)  

This is some math saying what is the chance of the zone we calculated earlier intersecting with a ring reigon which is not the same one as the out current one.  
![diffring.png](RMassets/diffring.png)

"But sTuUnNNtTt what if they are in the same ring????" 

Umm, we take them out back and pretend they never existed cause that is too complicated with literally no payoff. Fun fact. We do not NEED to be insanely precise for this integral, we can approximate them and take quite a few shortcuts here and achieve good enough results.  
One such approxiation is utilising Simpson's rule for approximating integrals. Another one is not calculating for the entire set instead only doing so for relevant reigons. These bring our times to calulate from heat death of the universe down to about 2 ish seconds. 

There are other aspects of this paper that I have also chosen to not consider due to them overcomplicating the math with not a siginificant enough return. One example of this is the Beta disribution.
![img.png](RMassets/betadist.png)

This is only accounted for when we are trying to find a closer stronghold in the same place as the candidate stronghold. However, this is quite unlikely due to the way strongholds spawn with the angling so we opt to pretend that this won't happen as it compicates the code and increases runtime. Both of which I cannot afford atp tbh. 

