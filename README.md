<div align="center">

# 📷 Secondgallery

A clean, lightweight, self-hosted photo gallery designed for tech-savvy photographers and photography enthusiasts, built with Flask.

![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=white) ![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)

</div>

<div align="center">
  <img src="/mockup.png?raw=true" alt="Mockup" width="700">
</div>

## Getting Started

### Installation

1. Clone the repo

```sh
 git clone https://github.com/S4kur4/secondgallery.git
```

2. Create username and password for managing photos

```sh
 /bin/bash account_init.sh
```
3. Modify `.env` to add your personal configuration

```
# (Optional) Your social media links
FACEBOOK_URL=https://facebook.com
INSTAGRAM_URL=http://instagram.com
X_URL=http://x.com
LINKEDIN_URL=
TELEGRAM_URL=
DISCORD_URL=
BEHANCE_URL=https://www.behance.net
YOUTUBE_URL=https://youtube.com
PINTEREST_URL=
GITHUB_URL=
```
```
# (Optional) Google Analytics ID or Umami ID
GOOGLE_ANALYTICS_ID=
UMAMI_WEBSITE_ID=
```
```
# (Optional) Cloudflare Turnstile key to protect login form
TURNSTILE_SITE_KEY=
TURNSTILE_SECRET_KEY=
```
```
# Website title and your personal information
# An string list is used in ABOUT_ME to control paragraphs, one value represents one paragraph
TITTLE='Vivian Kent Photography'
ABOUT_ME='[
"👋 Hey! Thanks for viewing my photographries!",
"My name is Vivian Kent and I am a photographer living in Sydney, Australia. I specialize in humanistic photography and film style.",
"Feel free to contact me by clicking on the link at the bottom of the page."
]'
```
```
# You can set the username and password directly here
# Note that the ADMIN_PASSWORD must be your password-hashed SHA256 value
ADMIN_USERNAME=admin
ADMIN_PASSWORD=
```
4.  Launch with `docker-compose`

```sh
docker-compose up -d
```

5. Use Nginx, Caddy and anyother popular web servers to point to `127.0.0.1:5001`

### Photo Management

Visit `/manage` to login and manage photos, and you can remove or bulk upload your photos.

<video src="https://github.com/user-attachments/assets/701ab063-a256-435b-ac5a-4f3a06aea8fa" controls width="600"></video>

## Support Me on Ko-fi

I create this project because I'm passionate about photography. If you'd like to support my work and help me dedicate more time to it, please consider supporting on Ko-fi. Thank you for your generosity!

<a href="https://ko-fi.com/s4kur4_" target="_blank">
    <img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Support me on Ko-fi" style="height:30px;">
</a>
