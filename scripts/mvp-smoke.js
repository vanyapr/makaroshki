#!/usr/bin/env node

const fs = require("fs");
const os = require("os");
const path = require("path");
let chromium;

try {
  ({ chromium } = require("playwright"));
} catch (error) {
  console.error("Playwright is required: npm install -D playwright");
  process.exit(1);
}

const repoRoot = path.resolve(__dirname, "..");
const messengerPath = path.join(repoRoot, "messenger.html");
const messengerUrl = "file://" + messengerPath.replace(/ /g, "%20");

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

async function openMessenger(context, url = messengerUrl) {
  const page = await context.newPage();
  await page.goto(url);
  await page.waitForLoadState("load");
  return page;
}

async function installProfile(page, options = {}) {
  const profile = Object.assign({
    clientId: await page.evaluate(() => window.MacaroniSupport.clientId),
    displayName: "Я",
    provider: "github",
    repo: "https://github.com/vanyapr/makaroshki",
    token: "",
    privacyAccepted: true,
    updatedAt: new Date().toISOString()
  }, options);

  await page.evaluate((value) => {
    localStorage.setItem("macaroni.profile.v1", JSON.stringify(value));
  }, profile);
  await page.reload();
  await page.waitForFunction(() => document.body.dataset.view === "app");
  return profile;
}

async function messageTexts(page) {
  return page.evaluate(() => [...document.querySelectorAll(".message-row .text")].map((node) => node.textContent));
}

async function testUnsupportedScreen(browser) {
  const page = await browser.newPage();
  await page.setContent(fs.readFileSync(messengerPath, "utf8"), { waitUntil: "load" });
  await page.waitForFunction(() => document.body.dataset.support === "unsupported");
  const title = await page.locator(".unsupported-title").textContent();
  assert(title.includes("недостаточно смешной"), "unsupported screen title is missing");
  await page.close();
}

async function testLocalMvpFlow(browser) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await openMessenger(context);

  await page.waitForFunction(() => document.body.dataset.support === "supported");
  assert(await page.locator(".setup .screen-title").textContent() === "Первый запуск", "first-run screen is missing");
  assert(await page.locator("[data-client-id]").first().textContent() === "SA6E", "CLIENT_ID is not rendered");

  await installProfile(page);
  await page.locator("#message-input").fill("MVP smoke: сварить макарошки");
  await page.locator("#composer-form").evaluate((form) => form.requestSubmit());
  await page.waitForFunction(() => [...document.querySelectorAll(".message-row .text")].some((node) => node.textContent.includes("MVP smoke")));

  let texts = await messageTexts(page);
  assert(texts.some((text) => text.includes("MVP smoke")), "sent message is not visible");

  await page.reload();
  await page.waitForFunction(() => document.body.dataset.view === "app");
  texts = await messageTexts(page);
  assert(texts.some((text) => text.includes("MVP smoke")), "message was lost after reload");

  await page.locator("#search-input").fill("макарошки");
  await page.waitForFunction(() => document.querySelector("#sync-status").textContent.includes("search: 1"));

  await page.locator("#open-settings").click();
  await page.waitForFunction(() => document.body.dataset.view === "settings");
  await page.locator("#settings-reindex").click();
  await page.waitForFunction(() => document.querySelector("#settings-index-status").textContent.includes("Индекс пересобран"));
  await page.locator("#settings-back").click();
  await page.waitForFunction(() => document.body.dataset.view === "app");
  texts = await messageTexts(page);
  assert(texts.some((text) => text.includes("MVP smoke")), "message was lost after reindex");

  await context.close();
}

async function testOutboxAndRetry(browser) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await openMessenger(context);
  await installProfile(page, { token: "bad-token-for-smoke" });

  await page.evaluate(() => {
    window.fetch = () => Promise.reject(new Error("smoke network fail"));
  });
  await page.locator("#message-input").fill("MVP smoke: outbox retry");
  await page.locator("#composer-form").evaluate((form) => form.requestSubmit());
  await page.waitForFunction(() => document.querySelector("#sync-status").textContent.includes("outbox: 1"));

  let outbox = await page.evaluate(() => window.MacaroniStorage.listOutbox());
  assert(outbox.length === 1, "failed send was not stored in outbox");

  await page.evaluate(() => {
    const profile = JSON.parse(localStorage.getItem("macaroni.profile.v1"));
    profile.token = "";
    localStorage.setItem("macaroni.profile.v1", JSON.stringify(profile));
    window.fetch = window.fetch;
  });
  await page.locator("#sync-refresh").click();
  await page.waitForFunction(() => document.querySelector("#sync-status").textContent.includes("outbox: 0"));
  outbox = await page.evaluate(() => window.MacaroniStorage.listOutbox());
  assert(outbox.length === 0, "retry did not clear outbox");

  const inboxFiles = await page.evaluate(() => window.MacaroniTestRepo.listFiles("inbox/").then((files) => files.map((file) => file.path)));
  assert(inboxFiles.some((file) => file.startsWith("inbox/K2XM/")), "retry did not write recipient inbox");

  await context.close();
}

async function testGitHubInboxReindex(browser) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await context.addInitScript(() => {
    const chatId = "chat_remote_inbox";
    const messageId = "2026-06-09T04-00-00.000Z_K2XM_remote1";
    const messagePath = "chats/" + chatId + "/messages/2026/06/09/" + messageId + ".json";
    const files = {
      "protocol.json": {
        name: "Macaroni Protocol",
        version: 1,
        created_at: "2026-06-09T04:00:00.000Z",
        message_format: "json",
        privacy: "public_by_design",
        features: { encryption: "optional", attachments: "url_only", deletion: "markers_only" }
      },
      "users/SA6E.json": {
        version: 1,
        id: "SA6E",
        display_name: "Я",
        created_at: "2026-06-09T04:00:00.000Z",
        meta: { client: "Macaroni Messenger JS 0.1.0" }
      },
      ["chats/" + chatId + "/meta.json"]: {
        version: 1,
        id: chatId,
        title: "МАМА",
        created_at: "2026-06-09T04:00:00.000Z",
        created_by: "K2XM",
        visibility: "repo",
        privacy: "public_by_design"
      },
      ["chats/" + chatId + "/members.json"]: {
        version: 1,
        chat_id: chatId,
        members: [
          { id: "SA6E", display_name: "SA6E", role: "member" },
          { id: "K2XM", display_name: "K2XM", role: "owner" }
        ]
      },
      ["inbox/SA6E/" + messageId + ".json"]: {
        version: 1,
        recipient: "SA6E",
        message_id: messageId,
        chat_id: chatId,
        message_path: messagePath,
        created_at: "2026-06-09T04:00:00.000Z"
      }
    };
    files[messagePath] = {
      version: 1,
      id: messageId,
      chat_id: chatId,
      type: "text",
      from: "K2XM",
      to: ["SA6E"],
      created_at: "2026-06-09T04:00:00.000Z",
      text: "Remote inbox hello",
      reply_to: null,
      attachments: [],
      meta: { client: "Macaroni Messenger JS 0.1.0" },
      signature: null
    };

    function fileResponse(repoPath) {
      const value = files[repoPath];
      if (!value) {
        return null;
      }

      return {
        path: repoPath,
        type: "file",
        sha: "sha-" + repoPath,
        content: btoa(unescape(encodeURIComponent(JSON.stringify(value))))
      };
    }

    function listResponse(repoPath) {
      if (repoPath === "chats") {
        return [{ path: "chats/" + chatId, type: "dir", sha: "sha-chat" }];
      }

      if (repoPath === "chats/" + chatId + "/messages") {
        return [];
      }

      if (repoPath === "inbox/SA6E") {
        return [{ path: "inbox/SA6E/" + messageId + ".json", type: "file", sha: "sha-inbox" }];
      }

      return null;
    }

    window.__macaroniFetchPaths = [];
    window.fetch = (url) => {
      const marker = "/contents/";
      const rawPath = String(url).slice(String(url).indexOf(marker) + marker.length).split("?")[0];
      const repoPath = decodeURIComponent(rawPath);
      window.__macaroniFetchPaths.push(repoPath);
      const data = listResponse(repoPath) || fileResponse(repoPath);
      const ok = !!data;
      return Promise.resolve({
        ok,
        status: ok ? 200 : 404,
        statusText: ok ? "OK" : "Not Found",
        text: () => Promise.resolve(JSON.stringify(ok ? data : { message: "Not Found" }))
      });
    };
  });

  const page = await openMessenger(context);
  await installProfile(page, { token: "fake-token-for-inbox-smoke" });
  await page.locator("#sync-refresh").click();
  try {
    await page.waitForFunction(() => [...document.querySelectorAll(".message-row .text")].some((node) => node.textContent.includes("Remote inbox hello")));
  } catch (error) {
    const debug = await page.evaluate(() => ({
      sync: document.querySelector("#sync-status").textContent,
      storage: document.querySelector("[data-storage-status]").textContent,
      fetchPaths: window.__macaroniFetchPaths,
      texts: [...document.querySelectorAll(".message-row .text")].map((node) => node.textContent)
    }));
    throw new Error("GitHub inbox reindex did not render message: " + JSON.stringify(debug));
  }

  const texts = await messageTexts(page);
  assert(texts.some((text) => text.includes("Remote inbox hello")), "GitHub inbox message was not indexed");

  await context.close();
}

async function testTwoClientRecipients(browser) {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "macaroni-mvp-smoke-"));
  const k2xmPath = path.join(tempDir, "messenger-k2xm.html");
  fs.writeFileSync(
    k2xmPath,
    fs.readFileSync(messengerPath, "utf8").replace('const CLIENT_ID = "SA6E";', 'const CLIENT_ID = "K2XM";')
  );

  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await openMessenger(context, "file://" + k2xmPath);
  await installProfile(page, { clientId: "K2XM", displayName: "K2XM" });

  const members = await page.evaluate(() => window.MacaroniTestRepo.listFiles("chats/").then((files) => {
    const membersFile = files.find((file) => /members\.json$/.test(file.path));
    return membersFile ? JSON.parse(membersFile.content).members.map((member) => member.id) : [];
  }));
  assert(members.join(",") === "K2XM,SA6E", "K2XM default chat members are wrong: " + members.join(","));

  await page.locator("#message-input").fill("MVP smoke: K2XM to SA6E");
  await page.locator("#composer-form").evaluate((form) => form.requestSubmit());
  await page.waitForFunction(() => [...document.querySelectorAll(".message-row .text")].some((node) => node.textContent.includes("K2XM to SA6E")));

  const inboxFiles = await page.evaluate(() => window.MacaroniTestRepo.listFiles("inbox/").then((files) => files.map((file) => file.path)));
  assert(inboxFiles.some((file) => file.startsWith("inbox/SA6E/")), "K2XM did not write SA6E inbox");

  await context.close();
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    await testUnsupportedScreen(browser);
    await testLocalMvpFlow(browser);
    await testOutboxAndRetry(browser);
    await testGitHubInboxReindex(browser);
    await testTwoClientRecipients(browser);
    console.log("MVP smoke passed");
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
