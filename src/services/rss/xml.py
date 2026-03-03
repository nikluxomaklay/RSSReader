from typing import Optional

from rss_parser.models.rss import RSS
from rss_parser.models.rss.channel import Channel
from rss_parser.models.rss.image import Image
from rss_parser.models.types import Tag


class FixedImage(Image):
    title: Optional[Tag[str]] = None
    "Describes the image, it's used in the ALT attribute of the HTML <img> tag when the channel is rendered in HTML."

    link: Optional[Tag[str]] = None
    "The URL of the site, when the channel is rendered, the image is a link to the site. (Note, in practice the image <title> and <link> should have the same value as the channel's <title> and <link>."  # noqa


class FixedImageChannel(Channel):
    image: Optional[Tag[FixedImage]] = None


class FixedImageRSS(RSS):
    channel: Tag[FixedImageChannel]
