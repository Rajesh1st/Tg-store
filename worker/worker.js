export default {
  fetch(request) {
    const url = new URL(request.url)
    const key = url.searchParams.get("start")
    const BOT = "YourBotUsername"

    if (!key) {
      return Response.redirect("https://t.me/" + BOT, 302)
    }

    return Response.redirect(
      `https://t.me/${BOT}?start=${key}`,
      302
    )
  }
}
