"""Curated feed presets for the AI Content Digest."""

from dataclasses import dataclass


@dataclass
class FeedSource:
    name: str
    url: str
    description: str


CATEGORIES: dict[str, list[FeedSource]] = {
    "AI & Machine Learning": [
        FeedSource("Simon Willison", "https://simonwillison.net/atom/everything/", "AI engineering, LLMs, open source"),
        FeedSource("Lilian Weng", "https://lilianweng.github.io/index.xml", "Deep dives into ML research (OpenAI)"),
        FeedSource("The Gradient", "https://thegradient.pub/rss/", "Long-form AI/ML analysis"),
        FeedSource("MIT News — AI", "https://news.mit.edu/topic/artificial-intelligence2/feed", "MIT AI research highlights"),
        FeedSource("Distill.pub", "https://distill.pub/rss.xml", "Clear explanations of ML concepts"),
        FeedSource("The Batch (deeplearning.ai)", "https://www.deeplearning.ai/the-batch/feed/", "Andrew Ng's weekly AI newsletter"),
        FeedSource("Hugging Face Blog", "https://huggingface.co/blog/feed.xml", "Open-source ML models and tools"),
        FeedSource("Google Research Blog", "https://blog.research.google/feeds/posts/default?alt=rss", "Google AI/ML research"),
        FeedSource("Towards Data Science", "https://towardsdatascience.com/feed", "Community-driven ML articles"),
        FeedSource("Machine Learning Mastery", "https://machinelearningmastery.com/feed/", "Practical ML tutorials"),
    ],
    "Tech & Engineering": [
        FeedSource("Hacker News (Top)", "https://hnrss.org/newest?points=100", "Top-voted tech stories"),
        FeedSource("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index", "In-depth tech journalism"),
        FeedSource("The Verge", "https://www.theverge.com/rss/index.xml", "Tech news and culture"),
        FeedSource("TechCrunch", "https://techcrunch.com/feed/", "Startup and tech industry news"),
        FeedSource("Wired", "https://www.wired.com/feed/rss", "Technology, science, culture"),
        FeedSource("IEEE Spectrum", "https://spectrum.ieee.org/feeds/feed.rss", "Engineering and applied science"),
        FeedSource("ACM TechNews", "https://technews.acm.org/rss/TechNews.xml", "Computing research digest"),
        FeedSource("The Pragmatic Engineer", "https://newsletter.pragmaticengineer.com/feed", "Software engineering insights"),
        FeedSource("Martin Fowler", "https://martinfowler.com/feed.atom", "Software architecture and design"),
        FeedSource("InfoQ", "https://feed.infoq.com/", "Enterprise software development"),
    ],
    "Science & Research": [
        FeedSource("Nature", "https://www.nature.com/nature.rss", "Leading multidisciplinary science journal"),
        FeedSource("Quanta Magazine", "https://www.quantamagazine.org/feed/", "Math, physics, biology, CS deep dives"),
        FeedSource("Science (AAAS)", "https://www.science.org/rss/news_current.xml", "Peer-reviewed research news"),
        FeedSource("Phys.org", "https://phys.org/rss-feed/", "Daily science and tech news"),
        FeedSource("New Scientist", "https://www.newscientist.com/feed/home/", "Accessible science reporting"),
        FeedSource("MIT Technology Review", "https://www.technologyreview.com/feed/", "Tech impact on society"),
        FeedSource("Scientific American", "https://www.scientificamerican.com/feed/", "Science for general audiences"),
        FeedSource("ScienceDaily", "https://www.sciencedaily.com/rss/all.xml", "Research news aggregator"),
        FeedSource("The Conversation", "https://theconversation.com/us/articles.atom", "Academic experts, public discourse"),
        FeedSource("Ars Technica — Science", "https://feeds.arstechnica.com/arstechnica/science", "Science-focused tech journalism"),
    ],
    "AI Safety & Alignment": [
        FeedSource("Anthropic Research", "https://www.anthropic.com/research/rss.xml", "Constitutional AI, interpretability, alignment"),
        FeedSource("Alignment Forum", "https://www.alignmentforum.org/feed.xml", "Technical AI alignment research"),
        FeedSource("Import AI (Jack Clark)", "https://importai.substack.com/feed", "Weekly AI policy & safety digest"),
        FeedSource("AI Snake Oil", "https://www.aisnakeoil.com/feed", "Skeptical AI analysis (Princeton)"),
        FeedSource("MIRI", "https://intelligence.org/feed/", "Machine Intelligence Research Institute"),
        FeedSource("Center for AI Safety", "https://www.safe.ai/feed", "AI existential risk research"),
        FeedSource("80,000 Hours", "https://80000hours.org/feed/", "High-impact career research, AI risk"),
        FeedSource("GovAI Blog", "https://www.governance.ai/feed", "AI governance and policy research"),
        FeedSource("Transformer Circuits", "https://transformer-circuits.pub/rss.xml", "Anthropic's mechanistic interpretability"),
        FeedSource("The Gradient — Safety", "https://thegradient.pub/tag/safety/rss/", "AI safety perspectives and analysis"),
    ],
    "Developer Experience": [
        FeedSource("GitHub Blog", "https://github.blog/feed/", "GitHub platform updates and engineering"),
        FeedSource("The Changelog", "https://changelog.com/feed", "Open source and software dev news"),
        FeedSource("Stripe Blog", "https://stripe.com/blog/feed.rss", "API design and developer platform excellence"),
        FeedSource("Vercel Blog", "https://vercel.com/atom", "Frontend platform and DX innovation"),
        FeedSource("Fly.io Blog", "https://fly.io/blog/feed.xml", "Infrastructure, distributed systems, DX"),
        FeedSource("Deno Blog", "https://deno.com/feed", "JavaScript runtime and web standards"),
        FeedSource("Supabase Blog", "https://supabase.com/blog/rss.xml", "Open source backend-as-a-service"),
        FeedSource("Render Blog", "https://render.com/blog/rss.xml", "Cloud platform and deployment"),
        FeedSource("Cloudflare Blog", "https://blog.cloudflare.com/rss/", "Edge computing, workers, web infra"),
        FeedSource("Fastly Blog", "https://www.fastly.com/blog/rss.xml", "CDN, edge, and web performance"),
    ],
    "Business & Startups": [
        FeedSource("Y Combinator Blog", "https://www.ycombinator.com/blog/rss/", "Startup advice from YC"),
        FeedSource("a16z Blog", "https://a16z.com/feed/", "Andreessen Horowitz tech/venture insights"),
        FeedSource("First Round Review", "https://review.firstround.com/feed.xml", "Tactical startup management advice"),
        FeedSource("Paul Graham Essays", "https://www.paulgraham.com/rss.html", "Startup philosophy and thinking"),
        FeedSource("Benedict Evans", "https://www.ben-evans.com/benedictevans?format=rss", "Tech industry macro analysis"),
        FeedSource("Stratechery", "https://stratechery.com/feed/", "Tech business strategy (Ben Thompson)"),
        FeedSource("The Generalist", "https://www.generalist.com/feed", "Deep dives into tech companies"),
        FeedSource("Lenny's Newsletter", "https://www.lennysnewsletter.com/feed", "Product, growth, and careers"),
        FeedSource("CB Insights", "https://www.cbinsights.com/research/feed/", "Data-driven tech market analysis"),
        FeedSource("Sequoia Capital", "https://www.sequoiacap.com/feed/", "Venture capital perspectives"),
    ],
}

CATEGORY_NAMES = list(CATEGORIES.keys())


def parse_selection(user_input: str, max_items: int) -> list[int]:
    """Parse user input like '1,3-5,8' or 'all' into 0-based indices.

    Returns sorted, deduplicated list of valid indices.
    """
    text = user_input.strip().lower()
    if not text:
        return []
    if text == "all":
        return list(range(max_items))

    indices = set()
    for part in text.split(","):
        part = part.strip()
        if "-" in part:
            try:
                start, end = part.split("-", 1)
                for i in range(int(start), int(end) + 1):
                    if 1 <= i <= max_items:
                        indices.add(i - 1)
            except ValueError:
                continue
        else:
            try:
                num = int(part)
                if 1 <= num <= max_items:
                    indices.add(num - 1)
            except ValueError:
                continue

    return sorted(indices)


def estimate_cost(num_articles: int) -> str:
    """Estimate API cost for summarizing articles with Sonnet 4.5.

    Sonnet 4.5: $3/1M input, $15/1M output.
    Average per article: ~600 input tokens + ~150 output tokens ≈ $0.004
    """
    cost_per_article = 0.004
    total = num_articles * cost_per_article
    return f"~{num_articles} API-Calls → geschätzte Kosten: ~${total:.2f} (Sonnet 4.5)"
