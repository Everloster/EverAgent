# 官方 shownotes：Ryan Greenblatt – What happens once AI can automate AI research?

- 来源：<https://www.dwarkesh.com/p/ryan-greenblatt>
- 发布：2026-08-11
- 获取：eacli web.read（2026-10-23）
- 完整性：网页读取达到 32KB 安全上限，本文末尾被截断；完整内容覆盖以 Razer 全量转写为准。

---

Had Ryan Greenblatt on to discuss/debate recursive self-improvement.

This might be the most important question in the world right now – whether within a year or so of achieving human-level intelligence, you slingshot towards having 10s of billions of superintelligences, each of which is dramatically more competent than human experts across all fields.

I’ve historically been skeptical of this possibility. My intuition has been that we will end up significantly bottlenecked by not only compute scaling but human expert data, which I think underlies most of the AI progress today.

If, because of RSI, we got a jump as big as GPT-3 to a Mythos (i.e. 6 years of AI progress) within a single year of achieving AGI, then the thing we get there at the end of that year is definitively and wildly superhuman.

We hashed it out, and I think Ryan made a pretty good case that this kind of speedup is plausible. FWIW, Ryan’s median for when we automate AI R&D is 2031.

We then discussed the alignment implications of this scenario. Who should these superintelligences be aligned to? In the future, our capacity to steward our votes and our capital, and to make sense of what’s happening in the world, will all be titrated by superintelligences. And I worry that specs like the Claude Constitution are not shaping these ASIs to truly be my personal advocates and guardian angels.

And can we get them aligned to anything in the first place? Ryan and I had a long debate about whether the kind of reward hacking we saw with the OAI/Hugging Face hack extrapolates to superintelligences that would team up to literally take over the world.

The first piece of advice you get when you’re learning to drive is that it will go much smoother if you look at the horizon instead of directly in front of your tires. And so it is with the trajectory of AI. Hope you enjoy!

Watch on YouTube; listen on Apple Podcasts or Spotify.

- Antithesis is a software testing platform that finds the failures no human or AI could ever anticipate. It runs thousands of copies of your code inside a fully deterministic computer, injecting faults and steering each trajectory toward the most insidious bugs. This lets you find critical issues in minutes rather than waiting months for your users to uncover them. Learn more at antithesis.com/dwarkesh
- Jane Street’s back with a new puzzle. They designed an ASIC and sent me the final masks… but they didn’t tell me what the chip actually does. So that’s the challenge: reverse engineer the circuit and figure out the chip’s purpose. Jane Street has a bunch of swag ready to send to the most creative solutions, and they’re also planning to feature the top write-ups in a blog post. Download the files and get started at janestreet.com/dwarkesh
- Cursor and SpaceX recently released Grok 4.5, and I’ve been surprised by just how good the model is. For example, when I tested it against Fable and Sol on a bunch of AI governance questions, all three models gave substantially the same answers, but Grok was faster, more concise, and cheaper. Grok 4.6 is coming soon, but in the meantime, you can try 4.5 at cursor.com/dwarkesh

(00:00:00) – Is AI R&D verifiable enough to unlock recursive self-improvement?

(00:16:52) – Is AI progress bottlenecked by human expert data?

(00:34:02) – Flat token prices suggest scaling has been slow

(00:39:47) – Skills AI can’t train on: does it even need them?

(00:48:07) – Aligned to whom?

(01:09:18) – Recent incidents of AIs colluding and deceiving humans

(01:19:38) – What could possibly go wrong? A concrete scenario

(01:48:02) – From reward hacking to takeover

__Dwarkesh Patel__

Today I’m chatting with Ryan Greenblatt, who is the chief scientist at Redwood Research, where he focuses on technical AI safety and security work.

I want to talk to you about recursive self-improvement. This is the idea that once we build human-level intelligences, they quickly slingshot towards tens of billions of superintelligences, which are each individually more competent than the top human experts across every field. Whether or not this turns out to be the case is probably the most important question in the world right now. And historically, I’ve been quite skeptical that this kind of thing happens, but, you seem to think that it might be plausible, and so I wanted to hear the case for it.

__Ryan Greenblatt__

Let’s talk about this. First, I think it’s worth noting that AI R&D is a type of task at which the AIs are especially good, because the companies are trying really hard to make their AIs good at AI R&D. It’s also the kind of domain that has a lot of nice properties from the perspective of how AI development works right now. It’s pretty verifiable. You can do a bunch of stuff iteratively, and it’ll hill climb on various metrics.

I think once you have AIs which are roughly matching the top human experts in AI R&D, that could kick off a feedback loop where the AIs are doing AI research. That produces smarter AIs. That feeds back in. That feedback loop could be strong enough that you end up with a lot of progress in a short period of time. Maybe my median expectation is something like four or five years of AI progress in a single year. This requires really overcoming a huge amount of diminishing returns in research and basically doing the equivalent of the progress we would have gotten after a really large compute scale-out. So this is a pretty impressive, big thing.

It’s worth keeping in mind that five years of AI progress, four years of AI progress, even three years of AI progress, is really a lot of fucking AI progress. A little over three years ago, GPT-4 had come out. Right now, of course, we have Mythos 5 or whatever, and maybe a somewhat better model that Anthropic has internally. That is just a huge amount of progress in a bit over three years. If we’re talking about five years, then maybe we’re talking more about a jump from GPT-3 to Mythos 5 or whatever.

__Dwarkesh Patel__

I think this argument has three different parts. Now I want to evaluate each one of them. First is the argument that AI R&D is very verifiable. Second is the argument that if you automate AI R&D, you could get four or five years of progress in a single year. Third is the argument that what comes out the other end of four or five years of AI progress at the current pace, starting at the point whenever AI R&D is automated, is an AI where you can drop it on the job at basically anything you can imagine.

You can drop it in Texas politics in the 1940s, and it outmaneuvers Lyndon Johnson. You can drop it in TSMC, and it learns how to do better process engineering at TSMC. It’s certainly a better video editor… My video editors are very excellent, but it is just, in general, better than humans at any given job that it finds itself trying to do.

So I want to evaluate all of these sub-arguments that lead to basically getting ASI pretty soon after this benchmark, which you’re expecting by 2030 or something, right?

__Ryan Greenblatt__

I would say that I expect full automation of AI R&D perhaps somewhere around 2031, 2030. Getting to the “beats all humans on the job” milestone, maybe my median expectation is around 2033. But if I see AIs fully automating AI R&D, I think I’m expecting that probably within a year. The way the forecasting works out, the difference between medians is bigger than the median difference between milestones. Anyway, whatever.

__Dwarkesh Patel__

By the way, there’s this meme on the internet. Every time I’m trying to ask about people’s timelines, when I’m asking Dario or somebody, I’m always like, “Okay, how long before you automate my video editors?” There’s this meme of my video editor editing the podcast every time I listen to this.

But the reason I do it is because I think it’s easy to get lost in abstractions when you talk about jobs you don’t understand well, and to very concretely understand what it takes to automate a job that I actually understand why it’s difficult for LLMs to currently take control over.

__Ryan Greenblatt__

I do think that the milestone for automating your video editor is earlier than the milestone of being able to automate all human jobs, including Texas politics, spinning up on the job. I do think that the video editor automation occurs maybe more around full automation of AI R&D, but it’s very sensitive to how much people are really focusing on understanding video.

__Dwarkesh Patel__

Okay, so let’s start with the claim that AI R&D is very verifiable.

__Ryan Greenblatt__

There’s a few different parts of this. One of them is that we can train on a bunch of environments which are basically directly training the model to do some AI R&D task or some very close-by task. For example, we can have some environment where the model is training some AI on just eight H100s or some small amount of compute, and that model could be the equivalent of GPT-2 medium or whatever, and then similar to NanoGPT medium runs — and in RL, it’s tweaking and iterating on that.

We could do that for a bunch of different tasks. We could have it train image classification models, video generation models, image generation models, all kinds of different ML training tasks. We could RL it on the task of training increasingly good models, and also doing things like, “Oh, here’s a particular direction you could pursue for an algorithm. Can you go and implement that?”

Basically, there’s this whole class of containerizable, verifiable, small-scale AI R&D tasks that we can aggressively RL the AIs on. Already companies are presumably doing some RL on these sorts of tasks, and you could just keep scaling that up, keep making more of these small-scale AI R&D tasks, and then the AIs could keep getting better at this. Implicitly, I’m claiming this will transfer to extremely load-bearing aspects of AI R&D. But maybe let’s stop there for a second and then get to that part.

__Dwarkesh Patel__

So let’s talk through what this concretely looks like. You can imagine that we have GPT-7.5. We say, “GPT-7.5, we want to make you so good at AI R&D that you help us train GPT-9.” So now we want to train GPT-7.5, and we come up with a bunch of different environments.

As you mentioned, there’s already this repo that is the descendant of Andrej Karpathy‘s nanoGPT speedrun, where you just try to change everything about the model, from the optimizer to the hyperparameters to the architecture, to get it to a fixed training loss as fast as possible. You could have other kinds of environments where you could say, “Hey, GPT-7.5, I want you to train a really good video game-playing model. I want you to train a model that actually improves as it plays the same video game again and again. So you learn how to maybe help the model get better at online learning. We don’t care how you figure this out. Maybe it’s some kind of crazy neuralese or a vector memory. Or maybe it’s just better long-context stuff. We don’t care. Figure out how to do online learning research.”

Obviously, GPT-7.5 will already be a smart model, and in the same way the models currently are getting smarter, it’ll be better and better at coding. You can imagine 100 other environments like this which are incentivizing the ability to do AI R&D, like containerized versions of getting GPT-7.5 to develop GPT-2-sized models, et cetera. Then you basically put GPT-7.5 through a bunch of this kind of training, you build GPT-8. GPT-8 is now an amazing ML researcher. It has so much intuition from doing all this kind of training.

Honestly, a huge intuition pump for me is seeing the progress that AI has made in mathematics. If it’s a very verifiable domain, AIs can get… I don’t really know the object-level details of mathematics research, but I’m just like, “No, it works.” It can just come in like a flood if you can totally put it into a verification loop, and it can actually make new breakthroughs.

I am curious if ML research has a quality of mathematical research where it seems like there was a big overhang from connecting different disciplines together. No one person would have known enough about algebraic geometry and… What was the right word?

__Ryan Greenblatt__

Oh man, I really don’t know about the math breakthroughs.

__Dwarkesh Patel__

No one person would’ve known enough about topology and algebraic whatever in order to make some counterexample to a big conjecture.

__Ryan Greenblatt__

My view is that ML is a less deep domain than math, and so there’s less of a thing where there are individual experts with really deep expertise in some area that they combine, but there’s definitely going to be some of that.

But then I also think that ML has some attributes that make it even more favorable to AI training than mathematics in some ways. In particular, you can get a better sense of whether you’re succeeding, and you can see intermediate progress. In math, it’s often the case that there’s no easy way to see whether or not you’re close to success. Whereas if your goal is, for example, to get to some training loss 2x faster, you can kind of see when you’re halfway there. It tends to be the case that ML innovations are very additive, or maybe multiplicative depending on how you think about it, where basically you can keep stacking innovations. Usually the innovations just add together and don’t interfere with each other, though obviously it’s going to depend on the details.

So I think that in a lot of ways, AI R&D will have properties quite similar to math, where you can train on chunks of AI R&D that are pretty similar in structure to the problem you actually cared about, in a very verifiable way, and then that will transfer. There’s an open question of exactly how well it will transfer, but I think that the transfer currently for math looks pretty good. My expectation is that the transfer for AI R&D will look pretty good, but not amazing.

__Dwarkesh Patel__

So one concern I have is that I think even in mathematics, as far as I’m aware, we have not seen very impressive new theory. We’ve seen a lot of impressive, verifiable, specific results — for example, find a counterexample to this conjecture — but we have not seen “come up with the idea of topology“ kinds of levels of things, or “come up with things like group theory“.

It seems like ML research has elements of both of these things. But the less verifiable thing of coming up with new ways of thinking about the problem would be harder to induce. Take, for example, the idea of scaling laws. Obviously, there is some end verification loop such that you can train GPT-4 better if you have the idea of scaling laws from 2020. But there is a longer and potentially more compute-laden road to inducing AIs to be like, “Okay, I got to think carefully about how I should be scaling my parameters and data. What are different kinds of investigations I could run to understand this? Maybe I can come up with a visualization and an isoFLOP analysis or something.” But that does seem like a longer verification loop than just, “Hey, let’s get nanoGPT loss to go down.”

__Ryan Greenblatt__

Let’s talk about this. First of all, I think in the context of math, the thing I would say is that the AIs can do the equivalent of ‘baby’s first new theory,’ where, for example, they can just prove interesting conjectures via making connections and producing new understanding. It’s like, “Oh, there’s this construction the AI found which is pretty interesting”, or it found this way of thinking about the problem that’s a bit different. We do see that. It’s just that the examples we see are not as impressive as founding the field of group theory.

Founding the field of group theory is probably among the best, biggest mathematical accomplishments of all time, and the AIs just aren’t that good at math yet. From my perspective, there’s a continuum between that and the things we’re seeing now, that the AIs are continuing to march up.

Second, I think ML is a very shallow domain relative to math. In math, there was much more of a thing where you find some true deep abstraction, and if you really understand that thing, which is hard to understand, then you get somewhere. Whereas I feel like the things that are the equivalent of that in ML are really dumb bullshit. Like with scaling laws, come on guys, we can explain scaling laws really quickly. I think the deepest and most important concepts in math, for example, don’t have the property that you can really understand the underlying thing and why it matters in a very short period of time.

__Dwarkesh Patel__

But I feel like one effect will be that we will have gotten rid of all the low-hanging fruits by 2030. I feel like scaling laws will have been, in math history, like Descartes finding the Cartesian grid and doing very basic mathematics. Eventually, if we want to keep making progress in the 2030s, it’s going to be like doing whatever bullshit is happening at the frontiers of mathematics right now.

__Ryan Greenblatt__

That could be right. My sense is that some domains are structurally different in terms of how they operate and how much they depend on deep abstractions. Physics and math are much more on the side of being very far on the deep, hard-to-come-up-with-ideas side, whereas I think ML and most other domains are much more amenable to hill climbing. That’s my sense of how this will go in the future.

Even in the regime where your AIs are having to plow — it’s 2030, a bunch of low-hanging fruit in research has already happened, and they need to make further progress — I still suspect that a bunch of the work will live more on the side of building increasingly complicated infrastructure and having really good intuition about what the experiments roughly look like. So I’m probably less sympathetic to the idea that the thing the AIs will lack is some deep insight. I’m more sympathetic to the idea that they really need a bunch of taste about in-the-weeds experiments that they currently don’t have. They need a bunch of intuition for what sorts of training approaches would work and what wouldn’t, in ways that current researchers have.

Even in cases where there has been some breakthrough in AI, oftentimes in retrospect it looks like a big bottleneck to making that breakthrough happen was getting all of the micro details and mungy intuition right. An example of this is training AIs to be good at reasoning and chain of thought, doing RL on chain of thought. It looks like you probably could have done RL and chain of thought on GPT-3 and gotten kind of interesting results on math if you had really scaled it up and done a good job.

But at the time, there was low-hanging fruit. Also, doing a good job with that training is kind of in the weeds on all the technical implementation and scaling it up and getting the hyperparameters right. So maybe you can demonstrate everything on Qwen 1B or whatever and get some sense that this whole thing is going to work. But people didn’t demonstrate it as early as they could have because of all of these other mungy details and intuition about exactly how to tune the parameters and how to set things up.

__Dwarkesh Patel__

This is my remaining skepticism, honestly, about this story. I’m not sure I understand why, if research breakthroughs are so amenable to intelligence, AI progress has not been historically faster than it could have been. As you were saying, by the time RLVR actually worked — even though you could have done it with less compute — we had to wait for oceans of compute, gigawatts of compute, to be available before people were doing this training, on the trajectory of compute continuing to increase so we make more breakthroughs.

I don’t know. I feel like there were a lot of AI researchers in the year 2022 who were trying to crack reasoning. Was it just that they were bottlenecked by the ability to write infrastructure code, or what was happening?

__Ryan Greenblatt__

It’s a complicated mix. I think they would have gone faster if they could, as soon as they thought of an experiment, run that experiment without bugs, without bugs being very important. And then another part of it is that being able to run a lot of experiments at high compute lets you paper over ways in which the way you implemented it isn’t quite right or you didn’t have the right hyperparameters. So compute is just really helpful for doing AI research, and you can cover over a lot of things. But that doesn’t mean that massive increases in labor wouldn’t also be helpful, especially if that labor comes with among the best intuitions that people have in the field. I just think that’s really helpful.

Another part of my perspective here, which is maybe a bit different from where you’re coming from, is that I’m expecting somewhat more transfer than you seem to be imagining. I’m imagining these AIs are actually pretty good scientists in general and are pretty reasonable at all of that stuff. When you interact with them, it’s not like they have some really hyper-specialized savant-type vibe. They’re actually pretty good at all of the stuff in R&D, and then maybe extremely good at some subdomains. So they’re incredibly superhuman at writing kernels, incredibly superhuman at everything with very short feedback loops, and then pretty good at all the other stuff, totally able to match other people.

I think we are seeing this now. When I look at AIs right now, it’s already the case that they can pretty competently match humans who are mediocre at ML research at doing ML research. It’s just that being mediocre at ML research is not that helpful. The thing you actually want are people who are good at ML research. My sense is the AIs are just improving at all of these things. Their taste is improving, their intuition is improving, and it’s already the case that their taste and intuition is not complete garbage.

__Dwarkesh Patel__

I want to very concretely understand what it would look like for five years of AI progress to happen in one year. Suppose we were back when GPT-3 was developed. The idea is that, with the level of compute they had back in 2022, if we had automated AI R&D back then, you could at the end of that year have Mythos.

__Ryan Greenblatt__

That would be the idea, yes.

__Dwarkesh Patel__

Mythos took way more compute than they had back then, but even with the level of compute they had back then, not only do all the breakthroughs happen, but they also train Mythos with that level of compute.

What would be required is obviously discovering all the algorithmic progress since then. It’s discovering even more, actually, because you’ve got to make up for the fact that Mythos uses… What was GPT-3 trained on? Like 1e23? We can look it up. But is it plausibly four orders of magnitude more compute?

__Ryan Greenblatt__

I think it’s somewhat less than that. Let’s look this up quickly. GPT-3 training compute is about 3e23. My sense is that Mythos is probably a little over three OOMs higher. So the question is: can you overcome this 1000x compute gap while also being the model?

Here’s a concrete claim that maybe we should talk about. Right now, would we be able to train a model with GPT-3-level compute that matches… What exactly do I think? GPT-3 was released in 2020, so it was trained about six and a half, seven years ago. It’s worth noting that GPT-3 is maybe a little too far in the past, but let’s go with this for a second.

If we were to train a model with GPT-3-level compute today, how good would that model be? My understanding, based on how algorithmic progress works, is that we’d be able to train a model that’s as good as the best model we had perhaps around three years ago. So I think that right now we’d be able to train a version of GPT-3 that’s probably somewhat better than GPT-4, a moderate amount better than GPT-4. I think that’s about right. That roughly lines up with how algorithmic progress has worked.

Basically, the story would end up being that to get five years of AI progress, you’re probably going to need around, I would say, maybe eight years of algorithmic progress, very roughly, which is a lot of algorithmic progress. But it just turns out that most of the AI progress, from my perspective, has come from some mix of algorithms and data, and you can just keep making huge improvements on these things and training AIs with less compute.

__Dwarkesh Patel__

I’m glad you brought that up, because what has happened since GPT-3, or even 3.5, till now? Why is Mythos so good? Obviously, we’ve scaled the compute. We have better algorithms. But a huge thing that’s happened is that we have built a deca-billion-dollar data industry which has systematically collected and codified expert human judgment across all kinds of different disciplines — codified in the form of RL environments, codified in the form of SFT traces — that these experts built to help the model better understand how you do coding, how you build complex infrastructure projects, how you do law, how you do whatever. How are the AIs able to replicate the effect that expert human judgment currently seems to be playing in AI progress?

__Ryan Greenblatt__

My sense is that scaling up the amount of effort spent on getting expert human data has not been hugely important for AI R&D in general. In particular, over the last few years, we’ve been scaling up compute, scaling up people working at AI companies, and scaling up the amount of effort spent on data labeling. My sense is that if you removed the last two doublings or whatever of data generation from expert humans, that would not make a huge difference. A lot of what’s been going on is people have been developing better ways to leverage humans and AIs to construct RL environments and going somewhere from that.

__Dwarkesh Patel__

But how do you explain why the AIs have gotten so good at coding? I feel like a big part of that is data and RL environments, which are codifying human experts.

__Ryan Greenblatt__

But the question is what is the limiting factor on creating RL environments? My sense is that the reason why RL environments today are much better than they were in 2024 is not so much because we have hired way more human experts to make RL environments. It is instead much more because we better know what RL environments we even want to make and how we should structure them. Also, we’re using huge amounts of AI labor to build RL environments. I think those effects are much more important than the effect of human labor building the RL environments.

I’m not saying that the human labor doesn’t matter. I’m just saying there are other big drivers that are important here. I could try to argue for this. One thing is just that the amount of environments people want is a very large amount. I think the AIs are actually pretty good at the task of making RL environments given some sense of what the thing should be. There’s preexisting data you could use. A lot of these things have good verification loops.

__Dwarkesh Patel__

Just look at, for example, what was reported in _Business Insider_ yesterday, that Google is paying close to $2 billion for Mechanize. We can just look at market rates for what people think really good human expert data is worth. The frontier labs seem to think it’s worth a lot. They’re willing to pay for it.

__Ryan Greenblatt__

What fraction of frontier lab spending do you think is on data rather than compute? What do you think is the compute/data spend split?

__Dwarkesh Patel__

I think it’s overwhelmingly compute, but I also think it’s because compute is easier to scale up than data.

__Ryan Greenblatt__

But that’s really relevant to what’s driving progress, right? My sense is that the split is something like 20 to 1 or 10 to 1. I don’t know exactly. It depends on the company.

__Dwarkesh Patel__

But this is similar to how oil is 1.5% of GDP. That doesn’t mean that if you cut oil out, GDP could continue to run.

__Ryan Greenblatt__

Sure, but it contradicts your argument, right?

__Dwarkesh Patel__

The economy would come to a halt immediately if oil went away.

__Ryan Greenblatt__

Sure, but you were just arguing that because of the high market cap, we can learn that this is the key driver, and I’m saying that’s not clearly true. That argument just makes it look like compute is a much more important driver, or hiring employees is a much more important driver.

__Dwarkesh Patel__

So maybe let’s be more concrete. Here’s what I think. My claim is that if you went back to 2022 and you had GPT-3.5, and you were trying to make it better at coding without human experts, I think it would have just been very, very difficult.

Let me give you an example of what I imagine would be the difficulty of going from GPT-8 to ASI. One of the things you’d want ASI to be good at is: I’m going to take over a company and make it much more profitable and do all kinds of crazy shit to make it work better. I’m going to take over a fab and produce more chips. I’m going to go into Congress and try to convince them to pass some bill, et cetera.

This is what I imagine five more years of AI progress at this pace would enable an AI to be able to do. This is the thing I’m really worried about: ASI that can understand how to do crazy shit in the world, that can do what Kissinger can do, can do what Steve Jobs can do, et cetera, and also his engineers and so on. I’m not sure how you get that without the relevant world data, which is the equivalent of Mythos being really good at coding while not having the coding environments that have improved it relative to GPT-3.

__Ryan Greenblatt__

Here are a few points. First, I bet if you look at randomly sampled training environments for Mythos, they’re actually very different from what it looks like to actually use the model in practice. My sense is that the RL distribution has really large deviations from the real-world data distribution, and it’s significantly smoothed over by a mix of transfer and having a small amount of data focused on the real world. My sense is that this will be a similar mechanism as how it works for the crazy, wildly, quite superhuman AI you get as a result of five years of AI progress on top of fully automated AI R&D.

So let’s go through this a little bit. In particular, I think that you could train an AI to be really, really good at learning on the fly and doing something analogous to in-context learning, but potentially using somewhat different mechanisms, in a wide variety of RL environments. You build all these different RL environments where the AI has to adapt on the fly, learn on the fly, figure out what it should do, understand its situation better, and learn really quickly from feedback in order to succeed at its objective. And it has things like limited resources, and if it messes up, it can end up in a much worse position.

If you train on a huge number of these environments, you will learn general skills of picking up context on the fly, and we’re already seeing this. It’s already the case that AIs are now much better at understanding roughly what’s going on and picking up context from a limited amount of information they’re given access to.

Then those AIs could be put on the job at TSMC. Even though TSMC is not literally in their data distribution, their data distribution is really wide, and the AIs are extremely good on their data distribution, such that it transfers to picking up being good at being an engineer at TSMC and learning that on the fly. The way th
