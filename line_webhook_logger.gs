// LINE Webhook UserID Logger
// 只記錄 userId，不發送任何訊息
// 部署為 Web App 後貼到 LINE Developers Console 的 Webhook URL

var SHEET_ID = "1beRWvy2HvWP9XlY4FZ60to9OUS-521iCU4-U7831Jxo";
var LINE_TOKEN = "zx47R1KXkO1csoByts8Y5XRYLzTfk5WVJSXr+kz4kDYwDmt9GNwEiFJsB0jo9BRleJbo3wYAQxa7DMpHoCpKKRxT7RtZcg2cNMnv+Qm6ypAKjEVCSFVxFC7b7MMnF9cbiJzh8QPAcprWusdgjs86eQdB04t89/1O/w1cDnyilFU=";

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var sheet = SpreadsheetApp.openById(SHEET_ID).getSheets()[0];

    data.events.forEach(function(event) {
      if (!event.source || !event.source.userId) return;

      var userId = event.source.userId;
      var eventType = event.type;
      var time = new Date(event.timestamp);
      var displayName = getDisplayName(userId);

      sheet.appendRow([
        Utilities.formatDate(time, "Asia/Taipei", "yyyy/MM/dd HH:mm:ss"),
        eventType,
        displayName,
        userId
      ]);
    });

    return ContentService
      .createTextOutput(JSON.stringify({ status: "ok" }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: "error", message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function getDisplayName(userId) {
  try {
    var response = UrlFetchApp.fetch(
      "https://api.line.me/v2/bot/profile/" + userId,
      { headers: { "Authorization": "Bearer " + LINE_TOKEN } }
    );
    return JSON.parse(response.getContentText()).displayName || userId;
  } catch (e) {
    return userId;
  }
}

// 測試用：確認 Web App 已上線
function doGet() {
  return ContentService.createTextOutput("LINE Webhook Logger is running.");
}
