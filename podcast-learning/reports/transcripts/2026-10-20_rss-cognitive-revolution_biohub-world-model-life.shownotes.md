# 官方 shownotes：A World Model of Life: Biohub's Alex Rives on Virtual Cells, Measurement, & the $1.8B Data Push

- 来源：<https://www.cognitiverevolution.ai/a-world-model-of-life-biohub-s-alex-rives-on-virtual-cells-measurement-the-1-8b-data-push>
- 发布：2026-10-20
- 获取：eacli web.read（2026-10-23）
- 完整性：网页读取达到 32KB 安全上限，本文末尾被截断；完整内容覆盖以 Razer 全量转写为准。

---

## Watch Episode Here

---

## Listen to Episode Here

---

## Show Notes

ℹ️

__The following notes are AI-generated, based on the episode transcript. Please listen to the episode for the full conversation.__

Alex Rives is Head of Science at Biohub. He started the ESM protein language model project at Meta's Fundamental AI Research lab and then co-founded EvolutionaryScale, whose team joined Biohub in November 2025. Nathan opens with Biohub's mission to cure all diseases. Does it mean "solving biology," or curing aging, or living forever? Alex calls himself "a practical person" and sets a concrete target: "a world without disease," meaning no cancer, no infectious disease, and no chronic or degenerative disease. Getting there, he argues, takes fundamental science to understand how disease works. It also takes technology that moves medicine past pills and small molecules toward programmable interventions that can "read and write the programs of biology."

Nathan offers his own two-part split of the challenge: first find the causal target, then design something that hits it. Alex calls that the classic drug-development framework and says it still has plenty of room to run with AI's help. He prefers a more information-theoretic view, though. Life is a program, cells execute rules encoded in the genome, and disease "unfolds in very regular ways" as part of that program. That framing explains his frank assessment of the current field: "the models that are being called virtual cells today, I just don't think they meet that definition of a model that could actually simulate the cell in a meaningful way." He says progress needs three things at once. The first is a better modeling paradigm, since the transformer (Attention Is All You Need) lacks the multi-scale structure a cell demands. The second is data at scale. The third, and most fundamental, is new tools to observe and measure what matters.

Nathan's naive outside view is that today's techniques would work if the data were good enough. Alex mostly agrees, in the limit: with infinite data and compute, all architectures become function approximators and the inductive bias falls away. Protein biology, with gene sequencing at scale, is close to that regime. That is why ESM and its successors (ESM-2/ESMFold, ESM3) worked. Cell biology is far from that regime, so inductive bias still matters. The long-term goal is "a world model of life," able to project a cell's state down to atomically resolved structures and let development unfold in silico, and Alex says plainly that this is far off. What he thinks is attainable within about five years is an information-level model of the cell: a probabilistic transition function from a cell state plus inputs to a distribution over next states.

The data for that model is the point of the Virtual Biology Initiative, which Biohub launched in April with a $500 million commitment. Two days before the recording, Biohub announced a $1.8 billion expansion. The new partners are the Department of Energy, which is putting in more than $500 million over five years through its Genesis Mission; the NIH, which will coordinate datasets from more than $500 million in prior federal investment; and Google DeepMind, Isomorphic Labs, and Meta, which are investing $300 million collectively (coverage: Axios, Endpoints). Alex expects the roadmap to emphasize contextual maps of cellular biology: spatial biology that places cells in tissue and links molecular measurements to imaging "at the scale of hundreds of billions or more cells."

Asked how to balance expensive, rich modalities against cheap, plentiful ones, Alex turns to the laser phase plate. It brings phase contrast to electron microscopy by using an intense standing-wave laser to shift the phase of the electron beam. Alex calls it "the most powerful standing-wave laser in the world." Biohub's own release describes it more conservatively as "one of the brightest lasers of its type in the world," first proposed more than 15 years ago by UC Berkeley's Holger Müller and Robert Glaeser, with Biohub backing it since 2021. The results appeared in _Science_ in June (see also Berkeley News and C&EN). The main application is cryo-electron tomography, where the extra contrast makes individual macromolecules visible inside the cell. For Alex this is Biohub's core belief in action: many paradigm shifts in science have come from new measurement technology, and the biggest difference between biology and other AI domains is how limited our ability to observe it still is.

That leads to the problem of scale. A single point mutation can cause disease, so a useful model has to bridge molecules, cells, tissues, and organisms. Alex insists that a real model of the cell includes the cell in context, not just cells in culture, and he describes Biohub's imaging work at each level. That includes whole-organism imaging of transparent zebrafish, where microscopes track every cell from the single-cell embryo to a developed organism (see Zebrahub). On the old "in mice" joke, Alex grants that model organisms mislead in both directions, producing false cures and hiding human mechanisms. His answer is transfer, not a perfect proxy. ESM and AlphaFold worked because they were trained across all of evolution, not just on human proteins. Across vertebrates the building blocks are conserved even though "the programs are completely rewired."

On the language-model recipe, Alex expects biology to follow the same principles. These are the self-supervised representation learning that Hinton, LeCun, and Bengio championed, made concrete by scaling laws, plus an elicitation stage and eventually RLVR (reinforcement learning with verifiable rewards). The catch is that biology is empirical. Math and code can be verified computationally, but biology needs "empirical AI" that proposes experiments, runs them, and learns from them in a recursive loop with the lab as the verifier. On timelines, he expects first drafts of cell-level atlases of health and disease within one to two years and a fairly comprehensive map within five. On electronic health records, he is cautious: without the right basis "what you're gonna learn is a bunch of correlations." On fusing biology and language into one latent space, he is openly undecided. Bridging data is scarce today, but "probably" eventually, and protein language models already learn features for biology "that we don't yet have language or words to describe." Asked about "a million Bryan Johnsons," he calls deep longitudinal human data immensely valuable but sees Biohub's lever at the technology layer. His own self-tracking? "I have a watch that tracks my sleep. That's about as far as it gets."

## Topics covered

_No timestamps are listed. Ad placement in the edit will shift every time, so topics appear in conversation order._

- Defining "cure all diseases": a world without disease, and programmable medicine
- The classic drug-development framework vs. an information-theoretic view of life as a program
- Why today's "virtual cells" fall short: modeling paradigm, data at scale, and measurement
- Inductive bias vs. the infinite-data limit; protein biology vs. cell biology
- A "world model of life" (far off) vs. a probabilistic cell-state transition model (about five years out)
- The Virtual Biology Initiative and the $1.8B expansion with DOE, NIH, Google DeepMind, Isomorphic Labs, and Meta
- The laser phase plate, cryo-electron tomography, and measurement as the engine of paradigm shifts
- Bridging scales: cells in context, Biohub's imaging work, whole-organism zebrafish imaging
- Model organisms, the "in mice" problem, organoids, and transfer across evolution
- Pre-training, elicitation, RLVR, and "empirical AI" with laboratory verification
- Long time horizons, and cell atlases of health and disease within one to five years
- Electronic health records: valuable for care, but "a bunch of correlations" without causal grounding
- Fused latent spaces for biology and language, and protein features with no names yet
- "A million Bryan Johnsons," continuous monitoring, and Alex's minimal self-tracking

## Resources

### Guest

- Alex Rives, Biohub bio
- @alexrives on X
- TIME100 AI 2026: Alex Rives
- EvolutionaryScale team joins Biohub

### Biohub and the Virtual Biology Initiative

- Biohub
- Open data for predictive AI models of biology: $1.8 billion committed (Oct 7, 2026)
- Virtual Biology Initiative launch, $500M (Apr 29, 2026)
- Axios on the expansion
- Endpoints on the expansion
- DOE Genesis Mission · NIH · Google DeepMind · Isomorphic Labs · Meta AI

### Measurement and imaging

- Laser phase plate cryo-EM breakthrough (Biohub)
- Laser phase plate improves structure determination of small proteins by cryo-EM (_Science_, 2026)
- Berkeley News on the laser phase plate
- C&EN: 15 years, flawless mirrors, and the brightest laser in the world
- Holger Müller, UC Berkeley
- Zebrahub tracks zebrafish development · Zebrahub data portal

### Models, papers, and ideas

- ESM-1b: Biological structure and function emerge from scaling unsupervised learning to 250 million protein sequences (_PNAS_, 2021)
- ESM-2 / ESMFold: Evolutionary-scale prediction of atomic-level protein structure with a language model (_Science_, 2023)
- ESM3: Simulating 500 million years of evolution with a language model (_Science_) · release post
- Highly accurate protein structure prediction with AlphaFold (_Nature_, 2021)
- Attention Is All You Need
- Scaling Laws for Neural Language Models
- Hinton, LeCun & Bengio, 2018 ACM Turing Award
- Tülu 3, which introduced the term RLVR
- How to Build the Virtual Cell with AI (Bunne et al., background reading)
- Bryan Johnson's Blueprint
- Organoids (link?)

- The AI-Powered Biohub: Mark Zuckerberg & Priscilla Chan
- The Evolution Revolution, with Brian Hie
- AI Lab Groups & Protein Model Interpretability, with James Zou
- AI:AM: "Virtual Cells Saturate at 2%"

## Quotes worth pulling

> "What we wanna do is really live in a world without disease."
>
> — Alex Rives

> "The models that are being called virtual cells today, I just don't think they meet that definition of a model that could actually simulate the cell in a meaningful way and actually really serve as an oracle for experimental biology."
>
> — Alex Rives

> "So in that sense, you could think of it as a world model, right? Kind of a world model of life, a world model of biology. I think we're very far from that."
>
> — Alex Rives

> "The cell is an information-processing machine, which has a genome which encodes the programs that run life."
>
> — Alex Rives

> "ESM and AlphaFold did not come from training a model just on human proteins. They really came from training a model across all of evolution… If you trained a model just on the human proteins, you wouldn't get an accurate predictive model."
>
> — Alex Rives

> "The programs are completely rewired, but they're built with the same building blocks."
>
> — Alex Rives

> "The things that we most want to know about biology, they're not represented in text. And they cannot be just derived from first principles or from what we already know."
>
> — Alex Rives

> "With biology, we're gonna have to build the systems that actually allow verification in the laboratory."
>
> — Alex Rives

> "I have a watch that tracks my sleep. That's about as far as it gets."
>
> — Alex Rives

__Sponsors:__

__Parallel:__ Parallel provides enterprise-grade web search APIs for AI agents, offering the optimal balance of quality, speed, and cost. Get started for free at https://parallel.ai/tcr

__OutSystems:__ OutSystems is the leading agentic systems platform that enables enterprises to engineer, orchestrate, and govern AI applications on a single unified platform. Learn more and see how it works at https://outsystems.com/tcr

__Tasklet:__ Tasklet empowers your business with AI agents that connect to your tools and automate recurring workflows with no code required. Visit https://tasklet.ai and use code cog rev for $50 in free credits

__CHAPTERS:__

(00:00) About the Episode

(03:58) Biohub's grand mission

(09:18) Limitations of virtual cells

(13:37) World models of biology

(19:35) The $1.8B data initiative (Part 1)

(19:40) Sponsors: Parallel | OutSystems

(22:58) The $1.8B data initiative (Part 2)

(29:29) Bridging multiscale biological systems

(35:44) Learning across model organisms (Part 1)

(35:49) Sponsor: Tasklet

(37:26) Learning across model organisms (Part 2)

(42:24) Pretraining and empirical AI

(52:04) Unifying biology and language

(56:32) Continuous monitoring and health

(59:30) Episode Outro

(01:03:11) Outro

__PRODUCED BY:__

https://aipodcast.ing

__SOCIAL LINKS:__

Website: https://www.cognitiverevolution.ai

Twitter (Podcast): https://x.com/cogrev_podcast

Twitter (Nathan): https://x.com/labenz

LinkedIn: https://linkedin.com/in/nathanlabenz/

Youtube: https://youtube.com/@CognitiveRevolutionPodcast

Apple: https://podcasts.apple.com/de/podcast/the-cognitive-revolution-ai-builders-researchers-and/id1669813431

Spotify: https://open.spotify.com/show/6yHyok3M3BjqzR0VB5MSyk

---

## Transcript

_This transcript is automatically generated; we strive for accuracy, but errors in wording or speaker identification may occur. Please verify key details when needed._

---

## Introduction

__[00:00]__ Hello, and welcome back to the Cognitive Revolution! Today my guest is Alex Rives, formerly co-founder and Chief Scientist at Evolutionary Scale, makers of the ESM series of models, and currently Head of Science at Biohub, the Chan Zuckerberg Initiative backed moonshot with the inspiring mission to cure or prevent all disease, which just announced a $1.8B expansion of the Virtual Biology Initiative, a data-generation effort that brings together the Department of Energy, the NIH, Google DeepMind, Isomorphic, and Meta. I opened by asking Alex what "curing all disease" means to him, and if I should expect to live much longer than the standard human lifespan. Calling himself "a practical person" in response, Alex described, not immortality, but a world without cancer, without infectious disease, and without chronic or degenerative conditions. From there, we get Alex's perspective on why today's virtual cell models haven't revolutionized medicine. The heart of the issue, Alex explains, is that our ability to observe what matters in biology is still very limited by the measurement technology we have available, and that as a result, we simply don't have the quality of data needed to represent the fine-grained causal structure that models presumably would be very happy to learn. Better architectures built on clever inductive biases can make the most of scarce data, such as in the extremely thoughtful use of physics in AlphaFold style models, and we do see real progress in next-token modeling of the biological code, but the available data is failing to capture critical information about how cells and tissues work. It's on this basis that Biohub is investing heavily in data, by opening new modalities, as they did with laser phase plate, an advance in microscopy that is allowing scientists to begin to directly see how individual proteins and other macromolecules interact inside the cell, and also by systematically building cell atlases that link molecular and imaging datasets across hundreds of billions of cells, representing both healthy and diseased states. The goal, over the next few years, is to build an information theoretic model of the cell, which effectively encodes the physical programs that run life, starting with a transition function that takes a cell or tissue state and a set of inputs and predicts a distribution of cell states at the next timestamp, ultimately building toward what Alex calls "a world model of life." This, of course, would support the use case I always dream of, which is answering the question: how do I push a pathologic state back to a healthy one, or in other words, effectively treat disease? Along the way, Alex describes how the LLM training paradigm applies to biology, his vision for "RLVR for biology", with lab verification, reacts to my proposal for "a million Bryan Johnsons", and ponders whether biological and language latent spaces will become deeply fused or remain separated by tool-calls, noting that the things we most want to know about biology are "novel concepts for which we don't yet have words and names." Finally, I asked Alex how he tracks his own health. He answered that he's so focused on Biohub research that he barely thinks about it, which surprised me, until I considered that, if he and the Biohub team are successful in creating the data layer needed to train highly generalizable biofoundation models, a little bit of timely, relevant personal health context might indeed be … all you need. With that, I hope you enjoy this look ahead toward a world model of life, with Alex Rives, Head of Science at Biohub.

## Main Episode

__[03:58]__ __Nathan Labenz:__ Alex Reeves, head of science at Biohub. Welcome to the cognitive revolution.

__[04:03]__ __Alex Rives:__ Thank you. Great to be here, Nathan.

__[04:04]__ __Nathan Labenz:__ Yeah. I'm excited for this conversation. So let's start with the big picture. Biohub has this grandiose mission, which I'm excited about, of curing all diseases Yes. Mean to you? Should I think of that as synonymous with another phrase people sometimes use as solving biology? Should I think of it as applying to aging? Should I... You know, are we living forever in your vision of the future? Like, how grand does this vision ultimately get?

__[04:30]__ __Alex Rives:__ Yeah. That's a great question.

__[04:31]__ __Nathan Labenz:__ How do

__[04:32]__ __Alex Rives:__ we define this? Well, I I I think I'm a practical person. Right? So I think about, you know, kinda what what is gonna be possible, I think, in a realistic time frame. And I think, you know, a good place to set our sights is to say that, you know, what we wanna do is is really live in a world without disease. Like, what would that mean? That would mean, you know, a world where there's not cancer, a world where there's not infectious disease, a world where there is not chronic disease or degenerative disease or, you know, all all the kinds of inflictions that have afflictions that have have have been, you know, really fundamental to to the human condition for a very long time. And, you know, I I think about that from a fundamental standpoint, like, you know, how do we how do we build the science that will, you know, really give us an understanding of of biology at a very deep and fundamental level that will under... Allow us to understand how disease works, that will allow us to to really identify the core mechanisms that will allow us to understand how how to detect disease, how to how how to how to intervene appropriately, and also kind of the the the technology. Right? So how can we go beyond kind of the current medical paradigm, which is, you know, kind of... And and I guess the therapeutic paradigm of of of kind of pills of of of molecules? You know, can we really go beyond that to far more programmable medicines that will will allow us to to really get to to the fundamentals of disease and really start to think about that as as as being able to to read and write the the programs of biology.

__[06:03]__ __Nathan Labenz:__ So sometimes when I've thought about this in the past, I've tried to break this grand challenge down into two slightly less grand challenges. One of them is just understanding the causal structure of what's going on inside our bodies so that we could know what leads to problems and therefore what our targets for intervention should be. And then the other one is like having identified a target, figuring out something that can actually have the desired effect. How would you... Know, is that a good taxonomy? How would you break that taxonomy of challenges down further if you want to? And which ones do we have kind of the most traction on, and and where do we need to catch up?

__[06:42]__ __Alex Rives:__ I mean, I think that's really the classic framework of drug development. So if you kind of think about, you know, how we think about creating a drug today, You know, we we think about physiology and disease. We try to identify really kind of a cause at the molecular level because that's where we can actually intervene today with the technology that we have. And then we really think about that problem of kind of, you know, finding and designing the intervention. And so, you know, that... That's that's kind of, I think, one paradigm. And I I think, you know, there's a there's a lot of progress that's that's still possible in that paradigm. So, you know, I I think that's that's kinda where we are today, of course. And and I think AI, you know, is is is is giving us, I think, really new potential to kind of look at each of the each of the parts of solving the... When you break the problem down that way, kind of each of the parts of solving it from that standpoint. But, I mean, I I think there's there's kind of also this this kind of, you know, more, I guess, like, information theoretic view on it that you might take where you can you can kind of think about, you know, life as as a program. Right? You can think about cells as as building living organisms, and you can really think about, you know, that that is a system of of rules, of code. And and you can think about, you know, what what what are the programs. Right? And, like, you know, how how do we... How could we read those programs? How could we start to start to rewrite those programs? And I think, you know, kind of thinking in in that way opens up a a wider aperture to to solving these problems. And I think a big part of kind of where we're trying to get with Biohub is is to really, you know, think about biology in that way, kind of create the tools for programmable biology, create the models that will allow us to understand biology in that context, you know, to really really start to understand how the cell works, both both both down to the molecular level, but also, you know, kinda kinda zooming out the cell in context and the the the, you know, the programs that that it runs to to build a living organism. And I think, you know, you could... You can really think as... Of disease as kind of a part of that. Right? It's it's really a part of the program. And and and if you think about it, you know, disease often unfolds in in very regular ways. So if we could kind of really understand that, I think it gives us really fundamentally new new tools to think about how how to make progress.

__[09:18]__ __Nathan Labenz:__ So I know you guys are working toward virtual cell models. Of course, there have been virtual cell models for a while. My general understanding of the state of play right now is, like, they don't work super well largely, and people have kind of said... Or, you know, have advanced different hypotheses, I guess, let's say, for why that would be the case. The one that I have found the most compelling is basically the data we have is just not that high of quality such that it may not contain the signals that the ML models would really need to learn what's really going on. How would you react to that hypothesis? Like, where where do you think the... Everything that's happened so far, like, why hasn't it taken us further than it has today?

__[10:05]__ __Alex Rives:__ Yeah. The, you know, the cell is incredibly complex. So I think I think you have to start there. You know? It's it's it's it's kind of like the right maybe meso scale for thinking about biology. But, you know, if you if you think about the cell, it's it's it's constituted by this just incredibly complex dynamic collection of of of matter, you know, where where kind of down to the level of individual atoms and and and and the interactions between between molecules. You know, those are those are... Those events are are determining of of of what happens at this... The the larger scale of the cell. And so... And and then... So so there's that kind of perspective, you know, building up from from, you know, the atomic resolution, kind of the first physical and chemical first principles. And then you can also kind of then think about the cell as as embedded within within, you know, living system, right, within within tissue, within physiology, within an organism, and sort of the complex programs that cells are able to execute to sense and respond to their environment, to communicate with each other, to, you know, really do these incredibly complicated and dynamic things. And so it's it's an immense immense challenge. And I think there are, you know, a number a number of limitations. So so so one is kind of, I think, you know, the models themselves, right, and just kind of having the right the right modeling approach and the right modeling paradigm. And, you know, we we have the transformer in in other areas of of AI, but the transformer kind of doesn't have that kind of multiscale structure that could could could represent those those different levels of of complexity. So there's there's kind of a question of of what's the right modeling paradigm. But then I think even more fundamental, there's the the question of of observation, observability, and measurement. And, you know, so much about the cell, you know, we just really can't measure. Sometimes we can't see it at all, And in many cases, kind of generating data at at scale would be really hard. And so if you you think about kind of many of the advances in science and biology, you know, they they really come from kind of having a new technology that that, you know, that that changes what we can measure, what we can observe. You know, the the the new powers to to to to see and observe biology, you know, can can really open up a new understanding of it. And so I I really think there's kind of three parts to really solving this problem. There's there's the modeling part. There's the there's the the the part of generating data at scale that's going to really reveal the the information architecture and the programs of the cell in in its in its kind of statistical structure. And then it's really, you know, the tools that we have to actually observe the cell and and and actually measure the things that that that matter. And I think you need to see progress on all three of those. And so, you know, the models that are being called virtual cells today, you know, I I just... I don't I don't think they meet that that definition of a model that that could actually simulate the cell in a meaningful way and actually really serve as an oracle for experimental biology.

__[13:38]__ __Nathan Labenz:__ Let's do one more beat on how you imagine modeling evolving. I guess my naive sort of outside view, just based on all the success that we've seen in AI and language modeling and otherwise, is just like, if we had enough good data, feels to me like today's techniques would probably work. Maybe you would disagree with that. If you would disagree with that, what sort of future model do you envision? How do you think we sort of encode the right inductive priors and and sort of how how much of a, like, actual Rube Goldberg machine is the model? Is it, like, trying to match up the actual cell with, like, all the little proteins bopping around and interacting with each other and modeling all those, like, microstates? Or, you know, a kind of naive black box thing would be like, I have a cell. I perturb it. Like, what's the next state? You know, kind of the more of an input output without worrying about all the the detailed mechanisms inside. Where do you think we land on modeling when this really starts to work?

__[14:41]__ __Alex Rives:__ Yeah. That's a that's a great question. So I should start by saying that, you know, I really think that kind of in the limit of, you know, data and can... The limit of infinite data and and compute, if you're thinking in limits, kind of all mark... Model architectures probably kinda end up being being the same. Right? They're just kind of function approximators. Right? And so if you have the right inputs and the outputs and you, you know, you learn a very, very good general function approximator, then then then in that sense and those limits, kind of the model architecture itself falls away. But I think I think in biology, you know, we're we're very far from that point. We're very far with some exceptions. Right? Like, with with protein biology, you know, we have gene sequencing at scale. You know, we really can kind of, you know, get closer and closer to kind of that limit of of of of infinite data. But for for cellular biology, you know, we're we're just so far from that right now. And I think historically, when you're far from that limit, you know, inductive bias becomes really important. When I think about, you know, a model, I mean, I I think where do we ultimately want to get? You know, we we want to get to a model of the cells. Kind of what I was saying before. You know, it it has that complexity at the molecular level. It has a representation of that. You know, it could, you know, imagine kind of being able to project out the the the the state of the cell down to down to the level of, you know, atomically resolved structures of its components. You know, it would have that. It would also really be able to model the cell at the level of its programs, and it would be able to, you know, predict. It it would be able to to allow allow development to to unfold, to allow the the the the the the interactions within tissue to unfold and and and tell you what would happen. So in that sense, you could think of it as a world model. Right? Kind of a world model of life, a a world model of biology. I think we're very far from that. So what I think is possible now is an information theoretic model of the cell. And I think that the the... There are, you know, really these programs that run life. They're encoded in the genome. And I think it's it's historically... You know, there's there's been these kinda two dual ways to think about biology. One is this kind of bottoms up first principles approach kind of trying to build it from the basic chemical and physical principles. But I think the other view that's been really productive is to kind of really think about the the emergent level of the informational model of this... Of the cell. You know, the cell is an information processing machine, which has a genome, which encodes the programs that run life. And I think I think that is the... That's the level of understanding of the cell that could be attainable via a... AI in in kind of the the the next five years, let's say. I think I think that we really have... You know, we're in the age of information theory at at scale. And in a sense, you know, we have these incredibly powerful methods which can can can perform... You know, they do pretrained. They they use self supervised on these, you know, vast datasets. And from from statistical patterns tha
