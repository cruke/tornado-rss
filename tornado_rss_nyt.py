import tornado.ioloop
import tornado.web
import feedparser
import urllib.parse
from bs4 import BeautifulSoup

# RSS Feeds
RSS_FEEDS = {
    "astro_awani": "https://rss.astroawani.com/rss/latest/public",
    "harian_metro": "http://www.hmetro.com.my/mutakhir.xml",
    "the_sun": "https://thesun.my/rss/local",
    "nyt": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "cnn": "http://rss.cnn.com/rss/cnn_topstories.rss"
}

class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Select News Source</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                h1 { color: darkblue; }
                a { display: block; padding: 10px; margin: 10px auto; width: 250px; background: #0073e6; color: white; text-decoration: none; border-radius: 5px; }
                a:hover { background: #005bb5; }
            </style>
        </head>
        <body>
            <h1>Pilih Sumber Berita Pilihan Anda</h1>
            <a href="/news?source=astro_awani">Astro Awani</a>
            <a href="/news?source=harian_metro">Harian Metro</a>
            <a href="/news?source=the_sun">The Sun</a>
            <a href="/news?source=nyt">New York Times</a>
            <a href="/news?source=cnn">CNN</a>
        </body>
        </html>
        """)

class NewsHandler(tornado.web.RequestHandler):
    def get(self):
        source = self.get_argument("source", None)
        if source not in RSS_FEEDS:
            self.redirect("/")
            return

        rss_url = RSS_FEEDS[source]
        feed = feedparser.parse(rss_url)
        articles = feed.entries[:10]  # Get latest 10 articles

        # HTML Content
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Berita {source.replace('_', ' ').title()}</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: auto; }}
                h1 {{ color: darkblue; text-align: center; }}
                .article {{ margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .article img {{ max-width: 100%; height: auto; display: block; margin: 10px 0; }}
                .article h2 {{ margin: 0; }}
                .article p {{ color: #555; }}
                .article a {{ text-decoration: none; color: #0073e6; }}
                .article a:hover {{ text-decoration: underline; }}
                .back-btn {{ display: block; text-align: center; margin: 20px auto; width: 150px; background: #0073e6; padding: 10px; color: white; border-radius: 5px; text-decoration: none; }}
                .back-btn:hover {{ background: #005bb5; }}
            </style>
        </head>
        <body>
            <h1>{source.replace('_', ' ').title()} News</h1>
            <a class="back-btn" href="/">← Kembali ke Laman Utama</a>
        """

        for entry in articles:
            title = entry.title
            link = entry.link
            summary = entry.summary if 'summary' in entry else "No summary available."

            # Extract image using BeautifulSoup
            soup = BeautifulSoup(summary, "html.parser")
            img_tag = soup.find("img")
            image_url = img_tag["src"] if img_tag else None

            # Remove image from summary text
            for img in soup.find_all("img"):
                img.decompose()
            clean_summary = soup.get_text()

            # Add article HTML
            html_content += f"""
            <div class="article">
                <h2><a href="{link}" target="_blank">{title}</a></h2>
                {'<img src="' + image_url + '" alt="Article Image">' if image_url else ''}
                <p>{clean_summary}</p>
            </div>
            """

        html_content += '<a class="back-btn" href="/">← Back to Home</a>'
        html_content += "</body></html>"

        self.write(html_content)

def make_app():
    return tornado.web.Application([
        (r"/", HomeHandler),
        (r"/news", NewsHandler),
    ], debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)  # Runs on http://localhost:8888
    print("Server started at http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
