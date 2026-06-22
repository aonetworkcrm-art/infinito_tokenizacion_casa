#!/usr/bin/env python3
"""
📰 Posts Públicos — Páginas HTML reales indexables por Google
=============================================================
Almacena posts publicados desde la DApp y los sirve como páginas HTML completas
con anuncios Monetag. Google puede indexar estas páginas.

Endpoints:
    POST /api/publish-post  → Guarda un post publicado
    GET  /api/posts          → Lista todos los posts publicados (JSON)
    GET  /posts/{slug}       → Sirve el HTML completo del post (indexable)
    GET  /sitemap.xml        → Sitemap para Google Search Console
    GET  /robots.txt         → Robots.txt para Google
"""

import os
import json
import logging
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import HTMLResponse

logger = logging.getLogger("posts")

# ─── Router con prefix /api para los endpoints internos ───
router = APIRouter(prefix="/api", tags=["Posts Públicos"])

# ─── Router SIN prefix para las URLs públicas que Google va a rastrear ───
public_router = APIRouter(tags=["Posts Públicos - URLs Públicas"])

# ─── Persistencia en archivo (Vercel /tmp/ dura horas, mucho mejor que RAM) ───
POSTS_FILE = "/tmp/published_posts.json"


def _load_posts() -> dict:
    """Carga posts desde el archivo de persistencia."""
    if os.path.exists(POSTS_FILE):
        try:
            with open(POSTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_posts(posts: dict):
    """Guarda posts en el archivo de persistencia."""
    try:
        os.makedirs(os.path.dirname(POSTS_FILE), exist_ok=True)
        with open(POSTS_FILE, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
    except (IOError, OSError):
        pass  # Si no se puede escribir, no es crítico


# ─── Modelos ───

class PublishPostRequest(BaseModel):
    slug: str = Field(..., description="Slug único del post (ej: guia-abogados-accidentes)")
    title: str = Field(..., description="Título del post")
    content: str = Field(..., description="Contenido en texto plano (párrafos separados por \\n\\n)")
    meta_description: str = Field("", description="Meta description para SEO")
    niche_name: str = Field("", description="Nombre del nicho")
    niche_cat: str = Field("", description="Categoría del nicho")
    cpc: float = Field(0, description="CPC promedio")
    keywords: str = Field("", description="Keywords separadas por coma")
    monetag_site_id: str = Field("", description="Site ID de Monetag para anuncios")
    author: str = Field("Proyecto Infinito", description="Autor del post")


class PublishPostResponse(BaseModel):
    success: bool
    slug: str
    url: str
    message: str


# ─── Construir HTML completo con Monetag ───

def build_post_html(post: dict) -> str:
    """Construye una página HTML completa con Monetag ads, lista para Google."""
    
    title = post.get("title", "Artículo")
    meta_desc = post.get("meta_description", title)
    content = post.get("content", "")
    niche = post.get("niche_name", post.get("niche_cat", "General"))
    slug = post.get("slug", "post")
    keywords = post.get("keywords", title)
    cpc = post.get("cpc", 0)
    monetag_id = post.get("monetag_site_id", "")
    author = post.get("author", "Proyecto Infinito")
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Dividir contenido en párrafos
    paragraphs = [p.strip() for p in content.split("\n") if p.strip()]
    
    # Construir body con anuncios Monetag intercalados
    body_html = ""
    for i, p in enumerate(paragraphs):
        body_html += f"      <p>{p}</p>\n"
        # Anuncio después del 3er párrafo
        if i == 2 and monetag_id:
            body_html += f"""      <div class="ad">
        <div class="ad-label">— Publicidad —</div>
        <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-{monetag_id}" data-ad-slot="1234567890" data-ad-format="auto"></ins>
        <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
      </div>\n"""
    
    # Script de Monetag en head
    monetag_head = ""
    if monetag_id:
        monetag_head = f"""    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-{monetag_id}" crossorigin="anonymous"></script>
    <script>
      (adsbygoogle = window.adsbygoogle || []).push({{}});
    </script>"""
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{keywords}">
    <meta name="robots" content="index, follow">
    <meta name="author" content="{author}">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_desc}">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="canonical" href="https://proyectoinfinito.com/posts/{slug}/">
    {monetag_head}
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        :root{{--bg:#0f0a06;--grn:#2d8a4e;--cy:#0891b2;--text:#d4d4d8;--dim:#78716c;--card:#1c1917;--border:rgba(45,138,78,0.10)}}
        body{{font-family:'Georgia','Times New Roman',serif;background:var(--bg);color:var(--text);line-height:1.9}}
        .container{{max-width:820px;margin:0 auto;padding:40px 24px}}
        h1{{font-family:'Segoe UI',sans-serif;font-size:32px;color:#e4e4e7;margin:0 0 8px}}
        .meta{{font-size:11px;color:var(--dim);margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid var(--border)}}
        .meta span{{margin-right:16px}}
        .intro{{font-size:16px;color:#a1a1aa;padding:20px;border-left:3px solid var(--grn);background:rgba(45,138,78,0.04);margin-bottom:28px}}
        p{{font-size:15px;color:#d4d4d8;margin:16px 0;line-height:1.9}}
        h2{{font-family:'Segoe UI',sans-serif;font-size:22px;color:var(--grn);margin:36px 0 14px;padding-bottom:8px;border-bottom:1px solid var(--border)}}
        .ad{{margin:24px 0;padding:16px;border:1px dashed rgba(245,158,11,0.2);text-align:center;background:rgba(245,158,11,0.02)}}
        .ad-label{{font-size:8px;color:var(--dim);text-transform:uppercase;letter-spacing:2px;margin-bottom:6px}}
        .cta{{margin:36px 0;padding:28px;border:1px solid rgba(45,138,78,0.2);text-align:center;background:rgba(45,138,78,0.03)}}
        .cta .btn{{display:inline-block;padding:10px 32px;border:1px solid var(--grn);color:var(--grn);text-decoration:none;font-size:11px;letter-spacing:2px;text-transform:uppercase}}
        .cta .btn:hover{{background:var(--grn);color:#000}}
        footer{{margin-top:48px;padding:20px 0;border-top:1px solid var(--border);text-align:center;font-size:10px;color:var(--dim)}}
        @media(max-width:768px){{.container{{padding:20px 12px}}h1{{font-size:24px}}p{{font-size:14px}}}}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="meta">
            <span>📂 {niche}</span>
            <span>💰 CPC: ${cpc}</span>
            <span>📅 {date}</span>
        </div>
        <div class="intro">{meta_desc}</div>
{body_html}
        <div class="cta">
            <p>¿Necesitas ayuda con {title}? Contáctanos para una consulta gratuita.</p>
            <a href="#" class="btn">Solicitar Consulta →</a>
        </div>
        <footer>
            <strong>PROYECTO INFINITO</strong> &mdash; Publicación sobre {niche}<br>
            Generado por Shadow Silo AI &middot; {date}
        </footer>
    </div>
</body>
</html>"""
    return html


# ─── Endpoints (con /api prefix) ───

@router.post("/publish-post", response_model=PublishPostResponse)
def publish_post(req: PublishPostRequest):
    """📤 Guarda un post y lo hace accesible como página HTML real (indexable por Google)."""
    
    slug = req.slug.strip().lower()
    if not slug:
        raise HTTPException(status_code=400, detail="Slug inválido")
    
    slug = "".join(c if c.isalnum() or c == "-" else "-" for c in slug).strip("-")
    if not slug:
        slug = f"post-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    post_data = {
        "slug": slug,
        "title": req.title,
        "content": req.content,
        "meta_description": req.meta_description,
        "niche_name": req.niche_name,
        "niche_cat": req.niche_cat,
        "cpc": req.cpc,
        "keywords": req.keywords,
        "monetag_site_id": req.monetag_site_id,
        "author": req.author,
        "published_at": datetime.now().isoformat(),
    }
    
    # Guardar en memoria y en disco
    posts = _load_posts()
    posts[slug] = post_data
    _save_posts(posts)
    
    url = f"/posts/{slug}/"
    
    return PublishPostResponse(
        success=True,
        slug=slug,
        url=url,
        message=f"Post '{req.title}' publicado en {url}",
    )


@router.get("/posts", response_model=dict)
def list_posts():
    """📋 Lista todos los posts publicados."""
    
    posts = _load_posts()
    posts_list = []
    for slug, data in posts.items():
        posts_list.append({
            "slug": slug,
            "title": data.get("title", slug),
            "niche": data.get("niche_name", ""),
            "cpc": data.get("cpc", 0),
            "published_at": data.get("published_at", ""),
            "url": f"/posts/{slug}/",
        })
    
    posts_list.sort(key=lambda p: p.get("published_at", ""), reverse=True)
    
    return {
        "count": len(posts_list),
        "posts": posts_list,
    }


# ─── Endpoints PÚBLICOS (sin /api prefix) — los que Google va a rastrear ───

@public_router.get("/posts/{slug:path}", response_class=HTMLResponse)
def serve_public_post(slug: str):
    """📄 Sirve un post como página HTML completa para Googlebot."""
    
    slug = slug.strip("/")
    if slug.endswith("/"):
        slug = slug[:-1]
    
    posts = _load_posts()
    post = posts.get(slug)
    
    if not post:
        raise HTTPException(status_code=404, detail=f"Post '{slug}' no encontrado")
    
    html = build_post_html(post)
    return HTMLResponse(content=html, status_code=200)


@public_router.get("/sitemap.xml", response_class=Response)
def public_sitemap():
    """🗺️ Sitemap.xml para Google Search Console."""
    
    posts = _load_posts()
    
    if not posts:
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
</urlset>"""
    else:
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""
        for slug, data in posts.items():
            lastmod = data.get("published_at", datetime.now().isoformat())[:10]
            xml += f"""  <url>
    <loc>https://proyectoinfinito.com/posts/{slug}/</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
"""
        xml += "</urlset>"
    
    return Response(content=xml, media_type="application/xml")


@public_router.get("/robots.txt", response_class=Response)
def public_robots():
    """🤖 Robots.txt para guiar a Google."""
    
    content = """User-agent: *
Allow: /
Sitemap: https://proyectoinfinito.com/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")


def get_published_count() -> int:
    """Retorna cuántos posts hay publicados."""
    return len(_load_posts())
