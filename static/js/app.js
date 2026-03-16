(() => {
  const scripts = ["/static/js/auth.js"];

  if (document.getElementById("chatForm")) {
    scripts.push("/static/js/chat.js");
  }
  if (document.getElementById("adminContainer")) {
    scripts.push("/static/js/admin.js");
  }

  scripts.forEach((src) => {
    if (document.querySelector(`script[src=\"${src}\"]`)) return;
    const tag = document.createElement("script");
    tag.src = src;
    document.body.appendChild(tag);
  });
})();
