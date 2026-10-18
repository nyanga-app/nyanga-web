// Sends visitors of the old workers.dev address to nyanga.page; everything else is the built site.
export default {
  fetch(request, env) {
    const url = new URL(request.url);
    if (url.hostname.endsWith(".workers.dev")) {
      url.protocol = "https:";
      url.hostname = "nyanga.page";
      url.port = "";
      return Response.redirect(url.toString(), 301);
    }
    return env.ASSETS.fetch(request);
  },
};
