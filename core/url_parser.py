from urllib.parse import urlparse
from typing import Optional, Dict

class URLParser:
    SUPPORTED_DOMAINS = {
        'youtube.com': 'youtube',
        'youtu.be': 'youtube',
        'tiktok.com': 'tiktok',
        'instagram.com': 'instagram',
        'facebook.com': 'facebook',
        'fb.watch': 'facebook',
        'twitter.com': 'twitter',
        'x.com': 'twitter',
        'vimeo.com': 'vimeo'
    }

    @staticmethod
    def parse_url(url: str) -> Optional[Dict[str, str]]:
        """
        Analiza una URL y determina la plataforma y el ID del video
        
        Args:
            url: URL del video
            
        Returns:
            Dict con la plataforma y metadata, o None si no es válida
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]

            # Encuentra la plataforma correspondiente
            platform = None
            for supported_domain, platform_name in URLParser.SUPPORTED_DOMAINS.items():
                if supported_domain in domain:
                    platform = platform_name
                    break

            if not platform:
                return None

            return {
                'platform': platform,
                'url': url,
                'domain': domain,
                'path': parsed.path
            }
        except Exception:
            return None

    @staticmethod
    def is_supported_url(url: str) -> bool:
        """
        Verifica si la URL es de una plataforma soportada
        """
        return URLParser.parse_url(url) is not None
