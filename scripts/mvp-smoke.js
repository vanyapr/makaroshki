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

async function openMessenger(context, url = messengerUrl, clientId = "SA6E") {
  if (clientId) {
    await context.addInitScript((value) => {
      localStorage.setItem("macaroni.client_id.v1", value);
    }, clientId);
  }

  const page = await context.newPage();
  await page.goto(url);
  await page.waitForLoadState("load");
  return page;
}

async function installProfile(page, options = {}) {
  const profile = Object.assign({
    clientId: await page.evaluate(() => window.MacaroniSupport.clientId),
    displayName: "Me",
    provider: "other",
    repo: "https://github.com/vanyapr/makaroshki",
    token: "",
    language: "en",
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
  assert(title.includes("not funny enough"), "unsupported screen title is missing");
  await page.close();
}

async function testGeneratedClientIdPersists(browser) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await openMessenger(context, messengerUrl, null);

  await page.waitForFunction(() => document.body.dataset.support === "supported");
  const firstId = await page.evaluate(() => ({
    support: window.MacaroniSupport.clientId,
    stored: localStorage.getItem("macaroni.client_id.v1"),
    rendered: document.querySelector("[data-client-id]").textContent
  }));
  assert(/^[ABCDEFGHJKLMNPQRSTUVWXYZ23456789]{4}$/.test(firstId.support), "generated CLIENT_ID has wrong shape");
  assert(firstId.support === firstId.stored, "generated CLIENT_ID was not saved to localStorage");
  assert(firstId.support === firstId.rendered, "generated CLIENT_ID was not rendered");

  await page.reload();
  await page.waitForFunction(() => document.body.dataset.support === "supported");
  const secondId = await page.evaluate(() => window.MacaroniSupport.clientId);
  assert(secondId === firstId.support, "generated CLIENT_ID did not survive reload");

  await context.close();
}

async function testPollingContract(browser) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await openMessenger(context);

  await page.waitForFunction(() => document.body.dataset.support === "supported");
  const intervals = await page.evaluate(() => {
    const baseProfile = {
      clientId: "SA6E",
      displayName: "Me",
      provider: "github",
      repo: "https://github.com/vanyapr/makaroshki",
      privacyAccepted: true
    };

    window.MacaroniPolling.start(baseProfile);
    window.MacaroniPolling.stop();

    return {
      withToken: window.MacaroniPolling.intervalForProfile(Object.assign({}, baseProfile, { token: "token" })),
      readOnly: window.MacaroniPolling.intervalForProfile(Object.assign({}, baseProfile, { token: "" }))
    };
  });

  assert(intervals.withToken === 30000, "GitHub polling interval with token is wrong");
  assert(intervals.readOnly === 60000, "GitHub read-only polling interval is wrong");
  assert(!fs.readFileSync(messengerPath, "utf8").includes("document.hidden"), "polling must not pause hidden tabs");

  await context.close();
}

async function testLanguageSettings(browser) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await openMessenger(context);
  await installProfile(page);

  assert(await page.locator("#open-settings").textContent() === "Settings", "default language is not English");
  await page.locator("#open-settings").click();
  await page.waitForFunction(() => document.body.dataset.view === "settings");
  await page.locator("#settings-language").selectOption("ru");
  await page.waitForFunction(() => document.documentElement.lang === "ru");
  assert(await page.locator(".settings-screen .screen-title").textContent() === "Настройки", "Russian settings title is missing");
  assert(await page.locator("#message-input").getAttribute("placeholder") === "Введите сообщение...", "Russian composer placeholder is missing");
  await page.locator("#settings-form button[type='submit']").click();
  await page.waitForFunction(() => document.body.dataset.view === "app");
  const storedRu = await page.evaluate(() => ({
    language: JSON.parse(localStorage.getItem("macaroni.profile.v1")).language,
    languageKey: localStorage.getItem("macaroni.language.v1")
  }));
  assert(storedRu.language === "ru", "Russian language was not saved in profile");
  assert(storedRu.languageKey === "ru", "Russian language was not saved in localStorage language key");

  await page.locator("#open-settings").click();
  await page.waitForFunction(() => document.body.dataset.view === "settings");
  await page.locator("#settings-language").selectOption("en");
  await page.waitForFunction(() => document.documentElement.lang === "en");
  await page.locator("#settings-form button[type='submit']").click();
  await page.waitForFunction(() => document.body.dataset.view === "app");
  assert(await page.locator("#open-settings").textContent() === "Settings", "English language was not restored");

  await context.close();
}

async function testLocalMvpFlow(browser) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await openMessenger(context);

  await page.waitForFunction(() => document.body.dataset.support === "supported");
  assert(await page.locator(".setup .screen-title").textContent() === "First Run", "first-run screen is missing");
  assert(await page.locator("[data-client-id]").first().textContent() === "SA6E", "CLIENT_ID is not rendered");

  await installProfile(page);
  await page.locator("#message-input").fill("MVP smoke: cook macaroni");
  await page.locator("#message-input").press("Enter");
  await page.waitForFunction(() => [...document.querySelectorAll(".message-row .text")].some((node) => node.textContent.includes("MVP smoke")));
  assert(await page.locator("#message-input").inputValue() === "", "Enter submit did not clear composer");

  await page.locator("#message-input").fill("MVP smoke: link https://example.com/makaroni.");
  await page.locator("#message-input").press("Enter");
  await page.waitForFunction(() => [...document.querySelectorAll(".message-row .text a")].some((node) => node.href === "https://example.com/makaroni"));
  const linkInfo = await page.evaluate(() => {
    const link = [...document.querySelectorAll(".message-row .text a")].find((node) => node.href === "https://example.com/makaroni");
    return link ? { text: link.textContent, target: link.target, rel: link.rel } : null;
  });
  assert(linkInfo && linkInfo.text === "https://example.com/makaroni", "message URL was not linkified safely");
  assert(linkInfo.target === "_blank", "message URL link target is wrong");
  assert(linkInfo.rel.includes("noreferrer"), "message URL link rel is wrong");

  let texts = await messageTexts(page);
  assert(texts.some((text) => text.includes("MVP smoke")), "sent message is not visible");

  await page.reload();
  await page.waitForFunction(() => document.body.dataset.view === "app");
  texts = await messageTexts(page);
  assert(texts.some((text) => text.includes("MVP smoke")), "message was lost after reload");

  await page.locator("#search-input").fill("macaroni");
  await page.waitForFunction(() => document.querySelector("#sync-status").textContent.includes("search: 1"));
  await page.waitForFunction(() => {
    const hit = document.querySelector("#message-list .search-hit");
    return hit && document.activeElement === hit;
  });
  const searchHit = await page.evaluate(() => {
    const hit = document.querySelector("#message-list .search-hit");
    return {
      exists: !!hit,
      focused: document.activeElement === hit,
      text: hit ? hit.textContent : ""
    };
  });
  assert(searchHit.exists, "search did not mark first result");
  assert(searchHit.focused, "search did not jump focus to first result");
  assert(searchHit.text.includes("macaroni"), "search highlighted the wrong result");

  await page.locator("#open-settings").click();
  await page.waitForFunction(() => document.body.dataset.view === "settings");
  await page.locator("#settings-reindex").click();
  await page.waitForFunction(() => document.querySelector("#settings-index-status").textContent.includes("Index rebuilt"));
  await page.locator("#settings-back").click();
  await page.waitForFunction(() => document.body.dataset.view === "app");
  texts = await messageTexts(page);
  assert(texts.some((text) => text.includes("MVP smoke")), "message was lost after reindex");

  await page.evaluate(async () => {
    const chat = await window.MacaroniTestRepo.createChat({
      title: "WORK",
      owner_id: "SA6E",
      owner_name: "Me",
      members: [
        { id: "SA6E", display_name: "Me", role: "owner" },
        { id: "K2XM", display_name: "MOM", role: "member" }
      ]
    });
    await window.MacaroniTestRepo.sendMessage({
      chat_id: chat.meta.id,
      from: "SA6E",
      to: ["K2XM"],
      text: "MVP smoke: work chat"
    });
    await window.MacaroniTestRepo.sendMessage({
      chat_id: chat.meta.id,
      from: "K2XM",
      to: ["SA6E"],
      text: "MVP smoke: author from members"
    });
  });
  await page.locator("#sync-refresh").click();
  await page.waitForFunction(() => [...document.querySelectorAll("#chat-list .chat-item")].some((node) => node.textContent.includes("WORK")));
  const workUnreadBeforeOpen = await page.evaluate(() => {
    const item = [...document.querySelectorAll("#chat-list .chat-item")].find((node) => node.textContent.includes("WORK"));
    const badge = item && item.querySelector(".unread-badge");
    return badge ? badge.textContent : null;
  });
  assert(workUnreadBeforeOpen === "1", "new incoming message did not create unread chat indicator");
  await page.locator("#chat-list .chat-item", { hasText: "WORK" }).click();
  await page.waitForFunction(() => document.querySelector("#chat-title").textContent.includes("WORK"));
  await page.waitForFunction(() => [...document.querySelectorAll(".message-row .text")].some((node) => node.textContent.includes("work chat")));
  const workUnreadAfterOpen = await page.evaluate(() => {
    const item = [...document.querySelectorAll("#chat-list .chat-item")].find((node) => node.textContent.includes("WORK"));
    const badge = item && item.querySelector(".unread-badge");
    return badge ? badge.textContent : null;
  });
  assert(workUnreadAfterOpen === null, "opening a chat did not clear unread indicator");
  await page.locator("#sync-refresh").click();
  await page.waitForFunction(() => document.querySelector("#sync-status").textContent.includes("sync: ok"));
  const workUnreadAfterReindex = await page.evaluate(() => {
    const item = [...document.querySelectorAll("#chat-list .chat-item")].find((node) => node.textContent.includes("WORK"));
    const badge = item && item.querySelector(".unread-badge");
    return badge ? badge.textContent : null;
  });
  assert(workUnreadAfterReindex === null, "reindex did not preserve read chat marker");
  texts = await messageTexts(page);
  assert(texts.some((text) => text.includes("work chat")), "dynamic chat selection did not render chat messages");
  await page.locator("#search-input").fill("mom");
  await page.waitForFunction(() => document.querySelector("#sync-status").textContent.includes("search: 1"));
  texts = await messageTexts(page);
  assert(texts.some((text) => text.includes("author from members")), "search did not match member display name");
  await page.locator("#search-input").fill("");
  await page.waitForFunction(() => document.querySelector("#sync-status").textContent.includes("search: off"));
  await page.locator("#chat-list .chat-item", { hasText: "MOM" }).click();
  await page.waitForFunction(() => document.querySelector("#chat-title").textContent.includes("MOM"));
  await page.locator("#sync-refresh").click();
  await page.waitForFunction(() => document.querySelector("#sync-status").textContent.includes("sync: ok"));
  assert((await page.locator("#chat-title").textContent()).includes("MOM"), "sync did not preserve selected chat");
  await page.locator("#message-input").fill("MVP smoke: message to mom after switch");
  await page.locator("#message-input").press("Enter");
  await page.waitForFunction(() => [...document.querySelectorAll(".message-row .text")].some((node) => node.textContent.includes("message to mom")));
  const switchedSend = await page.evaluate(async () => {
    const chats = await window.MacaroniStorage.listChats();
    const mama = chats.find((chat) => chat.title === "MOM");
    const work = chats.find((chat) => chat.title === "WORK");
    const mamaMessages = await window.MacaroniStorage.listMessages(mama.id);
    const workMessages = await window.MacaroniStorage.listMessages(work.id);
    return {
      inMama: mamaMessages.some((message) => message.text.includes("message to mom")),
      inWork: workMessages.some((message) => message.text.includes("message to mom"))
    };
  });
  assert(switchedSend.inMama, "message after switching chats was not stored in selected chat");
  assert(!switchedSend.inWork, "message after switching chats leaked into previous/default chat");

  page.once("dialog", async (dialog) => {
    assert(dialog.message() === "Chat title", "unexpected create chat prompt");
    await dialog.accept("NEW_CHAT");
  });
  await page.locator("#add-chat").click();
  await page.waitForFunction(() => document.querySelector("#chat-title").textContent.includes("NEW_CHAT"));
  await page.waitForFunction(() => [...document.querySelectorAll("#chat-list .chat-item")].some((node) => node.textContent.includes("NEW_CHAT")));
  const chats = await page.evaluate(() => window.MacaroniStorage.listChats());
  assert(chats.some((chat) => chat.title === "NEW_CHAT"), "created chat was not stored");

  const infoTextPromise = page.waitForEvent("dialog").then(async (dialog) => {
    const message = dialog.message();
    await dialog.accept();
    return message;
  });
  await page.locator("#chat-info").click();
  const infoText = await infoTextPromise;
  assert(infoText.includes("Chat: NEW_CHAT"), "chat info title is missing");
  assert(infoText.includes("chat_id:"), "chat info id is missing");
  assert(infoText.includes("members:"), "chat info members are missing");
  assert(infoText.includes("transport:"), "chat info transport is missing");
  assert(infoText.includes("outbox:"), "chat info outbox is missing");

  await page.evaluate(async () => {
    const chat = await window.MacaroniTestRepo.createChat({
      title: "FOREIGN_CHAT",
      owner_id: "K2XM",
      owner_name: "K2XM",
      members: [
        { id: "K2XM", display_name: "K2XM", role: "owner" }
      ]
    });
    await window.MacaroniTestRepo.sendMessage({
      chat_id: chat.meta.id,
      from: "K2XM",
      to: [],
      text: "MVP smoke: foreign chat"
    });
  });
  await page.locator("#sync-refresh").click();
  await page.waitForFunction(() => [...document.querySelectorAll("#chat-list .chat-item")].some((node) => node.textContent.includes("FOREIGN_CHAT")));
  await page.locator("#chat-list .chat-item", { hasText: "FOREIGN_CHAT" }).click();
  let dialogIndex = 0;
  page.on("dialog", async (dialog) => {
    dialogIndex += 1;
    if (dialogIndex === 1) {
      assert(dialog.message().includes("Chat: FOREIGN_CHAT"), "join info dialog title is missing");
      await dialog.accept();
      return;
    }
    if (dialogIndex === 2) {
      assert(dialog.message().includes("You are not in this chat"), "join confirm text is missing");
      await dialog.accept();
      return;
    }
    assert(dialog.message().includes("You were added to members.json"), "join success text is missing");
    await dialog.accept();
  });
  await page.locator("#chat-info").click();
  await page.waitForFunction(() => document.querySelector("#sync-status").textContent.includes("chat: joined"));
  const joinedMembers = await page.evaluate(async () => {
    const chat = (await window.MacaroniStorage.listChats()).find((item) => item.title === "FOREIGN_CHAT");
    const members = await window.MacaroniTestRepo.readJson(".macaroni/chats/" + chat.id + "/members.json");
    return members;
  });
  assert(joinedMembers, "join did not add current client to members.json");
  page.removeAllListeners("dialog");

  await page.evaluate(async () => {
    const chat = await window.MacaroniTestRepo.createChat({
      title: "MISSING_MEMBERS",
      owner_id: "K2XM",
      owner_name: "K2XM",
      members: [
        { id: "K2XM", display_name: "K2XM", role: "owner" }
      ]
    });
    const path = ".macaroni/chats/" + chat.meta.id + "/members.json";
    const request = indexedDB.open("macaroni-messenger", 3);
    await new Promise((resolve, reject) => {
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        const db = request.result;
        const tx = db.transaction("repoFiles", "readwrite");
        tx.objectStore("repoFiles").delete(path);
        tx.oncomplete = () => {
          db.close();
          resolve();
        };
        tx.onerror = () => reject(tx.error);
      };
    });
    await window.MacaroniTestRepo.sendMessage({
      chat_id: chat.meta.id,
      from: "K2XM",
      to: [],
      text: "MVP smoke: missing members"
    });
  });
  await page.locator("#sync-refresh").click();
  await page.waitForFunction(() => [...document.querySelectorAll("#chat-list .chat-item")].some((node) => node.textContent.includes("MISSING_MEMBERS")));
  await page.locator("#chat-list .chat-item", { hasText: "MISSING_MEMBERS" }).click();
  dialogIndex = 0;
  page.on("dialog", async (dialog) => {
    dialogIndex += 1;
    if (dialogIndex === 1) {
      assert(dialog.message().includes("K2XM (K2XM)"), "missing members fallback did not show creator");
      await dialog.accept();
      return;
    }
    if (dialogIndex === 2) {
      await dialog.accept();
      return;
    }
    await dialog.accept();
  });
  await page.locator("#chat-info").click();
  await page.waitForFunction(() => document.querySelector("#sync-status").textContent.includes("chat: joined"));
  const repairedMembers = await page.evaluate(async () => {
    const chat = (await window.MacaroniStorage.listChats()).find((item) => item.title === "MISSING_MEMBERS");
    return window.MacaroniTestRepo.readJson(".macaroni/chats/" + chat.id + "/members.json");
  });
  assert(repairedMembers.members.some((member) => member.id === "K2XM"), "missing members repair lost creator");
  assert(repairedMembers.members.some((member) => member.id === "SA6E"), "missing members repair did not add current client");

  await context.close();
}

async function testOutboxAndRetry(browser) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await openMessenger(context);
  await installProfile(page, { provider: "github", token: "bad-token-for-smoke" });

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
    profile.provider = "other";
    localStorage.setItem("macaroni.profile.v1", JSON.stringify(profile));
    window.fetch = window.fetch;
  });
  await page.locator("#sync-refresh").click();
  await page.waitForFunction(() => document.querySelector("#sync-status").textContent.includes("outbox: 0"));
  outbox = await page.evaluate(() => window.MacaroniStorage.listOutbox());
  assert(outbox.length === 0, "retry did not clear outbox");

  const inboxFiles = await page.evaluate(() => window.MacaroniTestRepo.listFiles(".macaroni/inbox/").then((files) => files.map((file) => file.path)));
  assert(inboxFiles.some((file) => file.startsWith(".macaroni/inbox/K2XM/")), "retry did not write recipient inbox");

  await context.close();
}

async function testGitHubRateLimitMessage(browser) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await openMessenger(context);
  await installProfile(page, { provider: "github", token: "" });

  await page.evaluate(() => {
    window.fetch = () => Promise.resolve({
      ok: false,
      status: 403,
      statusText: "Forbidden",
      text: () => Promise.resolve(JSON.stringify({
        message: "API rate limit exceeded for 127.0.0.1.",
        documentation_url: "https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"
      }))
    });
  });

  await page.locator("#sync-refresh").click();
  await page.waitForFunction(() => document.querySelector("[data-storage-status]").textContent.includes("rate limit"));
  const errorText = await page.locator("[data-storage-status]").first().textContent();
  assert(errorText.includes("rate limit"), "rate limit error was not shown");
  assert(!errorText.includes("Contents: Read and write"), "rate limit was misreported as token permissions");

  await context.close();
}

async function testGitHubInboxReindex(browser) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await context.addInitScript(() => {
    const chatId = "chat_remote_inbox";
    const messageId = "2026-06-09T04-00-00.000Z_K2XM_remote1";
    const messagePath = ".macaroni/chats/" + chatId + "/messages/2026/06/09/" + messageId + ".json";
    const files = {
      ".macaroni/protocol.json": {
        name: "Macaroni Protocol",
        version: 1,
        created_at: "2026-06-09T04:00:00.000Z",
        message_format: "json",
        privacy: "public_by_design",
        features: { encryption: "optional", attachments: "url_only", deletion: "markers_only" }
      },
      ".macaroni/users/SA6E.json": {
        version: 1,
        id: "SA6E",
        display_name: "Me",
        created_at: "2026-06-09T04:00:00.000Z",
        meta: { client: "Macaroni Messenger JS 0.1.0" }
      },
      ".macaroni/users/K2XM.json": {
        version: 1,
        id: "K2XM",
        display_name: "MOM",
        created_at: "2026-06-09T04:00:00.000Z",
        meta: { client: "Macaroni Messenger JS 0.1.0" }
      },
      [".macaroni/chats/" + chatId + "/meta.json"]: {
        version: 1,
        id: chatId,
        title: "MOM",
        created_at: "2026-06-09T04:00:00.000Z",
        created_by: "K2XM",
        visibility: "repo",
        privacy: "public_by_design"
      },
      [".macaroni/chats/" + chatId + "/members.json"]: {
        version: 1,
        chat_id: chatId,
        members: [
          { id: "SA6E", display_name: "SA6E", role: "member" },
          { id: "K2XM", display_name: "MOM", role: "owner" }
        ]
      },
      [".macaroni/inbox/SA6E/" + messageId + ".json"]: {
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
      if (repoPath === ".macaroni/chats") {
        return [{ path: ".macaroni/chats/" + chatId, type: "dir", sha: "sha-chat" }];
      }

      if (repoPath === ".macaroni/chats/" + chatId + "/messages") {
        return [];
      }

      if (repoPath === ".macaroni/users") {
        return [
          { path: ".macaroni/users/SA6E.json", type: "file", sha: "sha-user-sa6e" },
          { path: ".macaroni/users/K2XM.json", type: "file", sha: "sha-user-k2xm" }
        ];
      }

      if (repoPath === ".macaroni/inbox/SA6E") {
        return [{ path: ".macaroni/inbox/SA6E/" + messageId + ".json", type: "file", sha: "sha-inbox" }];
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
  await installProfile(page, { provider: "github", token: "fake-token-for-inbox-smoke" });
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
  const authors = await page.evaluate(() => [...document.querySelectorAll(".message-row .author")].map((node) => node.textContent));
  assert(authors.some((author) => author === "MOM:"), "GitHub inbox author name was not rendered: " + authors.join(", "));

  await context.close();
}

async function testGitHubSkipsUnchangedReindex(browser) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await context.addInitScript(() => {
    const chatId = "chat_unchanged_head";
    const messageId = "2026-06-09T07-00-00.000Z_K2XM_unchanged";
    const messagePath = ".macaroni/chats/" + chatId + "/messages/2026/06/09/" + messageId + ".json";
    const files = {
      ".macaroni/protocol.json": {
        name: "Macaroni Protocol",
        version: 1,
        created_at: "2026-06-09T07:00:00.000Z",
        message_format: "json",
        privacy: "public_by_design",
        features: { encryption: "optional", attachments: "url_only", deletion: "markers_only" }
      },
      ".macaroni/users/SA6E.json": {
        version: 1,
        id: "SA6E",
        display_name: "Me",
        created_at: "2026-06-09T07:00:00.000Z",
        meta: { client: "Macaroni Messenger JS 0.1.0" }
      },
      [".macaroni/chats/" + chatId + "/meta.json"]: {
        version: 1,
        id: chatId,
        title: "UNCHANGED_HEAD",
        created_at: "2026-06-09T07:00:00.000Z",
        created_by: "K2XM",
        visibility: "repo",
        privacy: "public_by_design"
      },
      [".macaroni/chats/" + chatId + "/members.json"]: {
        version: 1,
        chat_id: chatId,
        members: [
          { id: "SA6E", display_name: "SA6E", role: "member" },
          { id: "K2XM", display_name: "K2XM", role: "owner" }
        ]
      }
    };
    files[messagePath] = {
      version: 1,
      id: messageId,
      chat_id: chatId,
      type: "text",
      from: "K2XM",
      to: ["SA6E"],
      created_at: "2026-06-09T07:00:00.000Z",
      text: "Unchanged head hello",
      reply_to: null,
      attachments: [],
      meta: { client: "Macaroni Messenger JS 0.1.0" },
      signature: null
    };

    function encodeJson(value) {
      return btoa(unescape(encodeURIComponent(JSON.stringify(value))));
    }

    function fileResponse(repoPath) {
      const value = files[repoPath];
      return value ? { path: repoPath, type: "file", sha: "sha-" + repoPath, content: encodeJson(value) } : null;
    }

    function listResponse(repoPath) {
      if (repoPath === ".macaroni/chats") {
        return [{ path: ".macaroni/chats/" + chatId, type: "dir", sha: "sha-chat" }];
      }
      if (repoPath === ".macaroni/chats/" + chatId + "/messages") {
        return [{ path: ".macaroni/chats/" + chatId + "/messages/2026", type: "dir", sha: "sha-y" }];
      }
      if (repoPath === ".macaroni/chats/" + chatId + "/messages/2026") {
        return [{ path: ".macaroni/chats/" + chatId + "/messages/2026/06", type: "dir", sha: "sha-m" }];
      }
      if (repoPath === ".macaroni/chats/" + chatId + "/messages/2026/06") {
        return [{ path: ".macaroni/chats/" + chatId + "/messages/2026/06/09", type: "dir", sha: "sha-d" }];
      }
      if (repoPath === ".macaroni/chats/" + chatId + "/messages/2026/06/09") {
        return [{ path: messagePath, type: "file", sha: "sha-message" }];
      }
      if (repoPath === ".macaroni/inbox/SA6E" || repoPath === ".macaroni/users") {
        return [];
      }
      return null;
    }

    window.__macaroniRequestLog = [];
    window.fetch = (url) => {
      const textUrl = String(url);
      window.__macaroniRequestLog.push(textUrl);

      if (textUrl.includes("/commits/main")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          statusText: "OK",
          text: () => Promise.resolve(JSON.stringify({ sha: "remote-head-1" }))
        });
      }

      const marker = "/contents/";
      const rawPath = textUrl.slice(textUrl.indexOf(marker) + marker.length).split("?")[0];
      const repoPath = decodeURIComponent(rawPath);
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
  await installProfile(page, { provider: "github", token: "fake-token-for-head-smoke" });
  try {
    await page.waitForFunction(() => [...document.querySelectorAll(".message-row .text")].some((node) => node.textContent.includes("Unchanged head hello")));
  } catch (error) {
    const debug = await page.evaluate(() => ({
      sync: document.querySelector("#sync-status").textContent,
      storage: document.querySelector("[data-storage-status]").textContent,
      requests: window.__macaroniRequestLog,
      texts: [...document.querySelectorAll(".message-row .text")].map((node) => node.textContent)
    }));
    throw new Error("GitHub unchanged-head smoke did not render message: " + JSON.stringify(debug));
  }

  const before = await page.evaluate(() => ({
    commits: window.__macaroniRequestLog.filter((url) => url.includes("/commits/main")).length,
    contents: window.__macaroniRequestLog.filter((url) => url.includes("/contents/")).length
  }));

  await page.locator("#sync-refresh").click();
  await page.waitForFunction((count) => window.__macaroniRequestLog.filter((url) => url.includes("/commits/main")).length > count, before.commits);
  await page.waitForFunction(() => document.querySelector("#sync-status").textContent.includes("sync: ok"));

  const after = await page.evaluate(() => ({
    commits: window.__macaroniRequestLog.filter((url) => url.includes("/commits/main")).length,
    contents: window.__macaroniRequestLog.filter((url) => url.includes("/contents/")).length
  }));

  assert(after.commits > before.commits, "unchanged sync did not check remote head");
  assert(after.contents === before.contents, "unchanged sync still walked contents API");

  await context.close();
}

async function testGitHubReadOnlyMode(browser) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await context.addInitScript(() => {
    const chatId = "chat_readonly";
    const messageId = "2026-06-09T06-30-00.000Z_K2XM_readonly";
    const messagePath = ".macaroni/chats/" + chatId + "/messages/2026/06/09/" + messageId + ".json";
    const files = {
      ".macaroni/protocol.json": {
        name: "Macaroni Protocol",
        version: 1,
        created_at: "2026-06-09T06:30:00.000Z",
        message_format: "json",
        privacy: "public_by_design",
        features: { encryption: "optional", attachments: "url_only", deletion: "markers_only" }
      },
      [".macaroni/chats/" + chatId + "/meta.json"]: {
        version: 1,
        id: chatId,
        title: "PUBLIC_READONLY",
        created_at: "2026-06-09T06:30:00.000Z",
        created_by: "K2XM",
        visibility: "repo",
        privacy: "public_by_design"
      },
      [".macaroni/chats/" + chatId + "/members.json"]: {
        version: 1,
        chat_id: chatId,
        members: [
          { id: "SA6E", display_name: "SA6E", role: "member" },
          { id: "K2XM", display_name: "K2XM", role: "owner" }
        ]
      }
    };
    files[messagePath] = {
      version: 1,
      id: messageId,
      chat_id: chatId,
      type: "text",
      from: "K2XM",
      to: ["SA6E"],
      created_at: "2026-06-09T06:30:00.000Z",
      text: "Read-only public hello",
      reply_to: null,
      attachments: [],
      meta: { client: "Macaroni Messenger JS 0.1.0" },
      signature: null
    };

    function encodeJson(value) {
      return btoa(unescape(encodeURIComponent(JSON.stringify(value))));
    }

    function decodeJson(value) {
      return JSON.parse(decodeURIComponent(escape(atob(value))));
    }

    function fileResponse(repoPath) {
      const value = files[repoPath];
      return value ? { path: repoPath, type: "file", sha: "sha-" + repoPath, content: encodeJson(value) } : null;
    }

    function listResponse(repoPath) {
      if (repoPath === ".macaroni/chats") {
        return [{ path: ".macaroni/chats/" + chatId, type: "dir", sha: "sha-chat" }];
      }
      if (repoPath === ".macaroni/chats/" + chatId + "/messages") {
        return [{ path: ".macaroni/chats/" + chatId + "/messages/2026", type: "dir", sha: "sha-y" }];
      }
      if (repoPath === ".macaroni/chats/" + chatId + "/messages/2026") {
        return [{ path: ".macaroni/chats/" + chatId + "/messages/2026/06", type: "dir", sha: "sha-m" }];
      }
      if (repoPath === ".macaroni/chats/" + chatId + "/messages/2026/06") {
        return [{ path: ".macaroni/chats/" + chatId + "/messages/2026/06/09", type: "dir", sha: "sha-d" }];
      }
      if (repoPath === ".macaroni/chats/" + chatId + "/messages/2026/06/09") {
        return [{ path: messagePath, type: "file", sha: "sha-message" }];
      }
      if (repoPath === ".macaroni/inbox/SA6E") {
        return [];
      }
      return null;
    }

    window.__macaroniReadOnlyWrites = [];
    window.fetch = (url, options = {}) => {
      const marker = "/contents/";
      const rawPath = String(url).slice(String(url).indexOf(marker) + marker.length).split("?")[0];
      const repoPath = decodeURIComponent(rawPath);
      if (options.method === "PUT") {
        if (options.headers && options.headers.Authorization) {
          const body = JSON.parse(options.body || "{}");
          const value = decodeJson(body.content || "");
          files[repoPath] = value;
          window.__macaroniReadOnlyWrites.push({ path: repoPath, value });
          return Promise.resolve({
            ok: true,
            status: 200,
            statusText: "OK",
            text: () => Promise.resolve(JSON.stringify({ content: { path: repoPath, sha: "sha-written-" + repoPath } }))
          });
        }

        return Promise.resolve({
          ok: false,
          status: 403,
          statusText: "Forbidden",
          text: () => Promise.resolve(JSON.stringify({ message: "read only" }))
        });
      }
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
  await installProfile(page, { provider: "github", token: "" });
  await page.locator("#sync-refresh").click();
  await page.waitForFunction(() => [...document.querySelectorAll(".message-row .text")].some((node) => node.textContent.includes("Read-only public hello")));
  assert((await page.locator("#sync-status").textContent()).includes("GitHub read-only"), "read-only transport label is missing");

  await page.locator("#message-input").fill("Read-only write attempt");
  await page.locator("#composer-form").evaluate((form) => form.requestSubmit());
  await page.waitForFunction(() => document.querySelector("#sync-status").textContent.includes("outbox: 1"));
  const outbox = await page.evaluate(() => window.MacaroniStorage.listOutbox());
  assert(outbox.length === 1, "read-only send was not kept in outbox");

  await page.locator("#open-settings").click();
  await page.waitForFunction(() => document.body.dataset.view === "settings");
  await page.locator("#settings-token").fill("fake-token-after-readonly");
  await page.locator("#settings-form").evaluate((form) => form.requestSubmit());
  await page.waitForFunction(() => document.querySelector("#sync-status").textContent.includes("outbox: 0"));

  const retried = await page.evaluate(async () => ({
    outbox: await window.MacaroniStorage.listOutbox(),
    writes: window.__macaroniReadOnlyWrites
  }));
  assert(retried.outbox.length === 0, "token save did not drain outbox");
  assert(retried.writes.some((write) => /^\.macaroni\/chats\/chat_readonly\/messages\/\d{4}\/\d{2}\/\d{2}\/.+\.json$/.test(write.path)), "token save did not write queued message");

  await context.close();
}

async function testGitHubSendWrites(browser) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  await context.addInitScript(() => {
    const chatId = "chat_remote_send";
    const files = {
      ".macaroni/protocol.json": {
        name: "Macaroni Protocol",
        version: 1,
        created_at: "2026-06-09T04:30:00.000Z",
        message_format: "json",
        privacy: "public_by_design",
        features: { encryption: "optional", attachments: "url_only", deletion: "markers_only" }
      },
      ".macaroni/users/SA6E.json": {
        version: 1,
        id: "SA6E",
        display_name: "Me",
        created_at: "2026-06-09T04:30:00.000Z",
        meta: { client: "Macaroni Messenger JS 0.1.0" }
      },
      [".macaroni/chats/" + chatId + "/meta.json"]: {
        version: 1,
        id: chatId,
        title: "MOM",
        created_at: "2026-06-09T04:30:00.000Z",
        created_by: "SA6E",
        visibility: "repo",
        privacy: "public_by_design"
      },
      [".macaroni/chats/" + chatId + "/members.json"]: {
        version: 1,
        chat_id: chatId,
        members: [
          { id: "SA6E", display_name: "SA6E", role: "owner" },
          { id: "K2XM", display_name: "K2XM", role: "member" }
        ]
      }
    };

    function encodeJson(value) {
      return btoa(unescape(encodeURIComponent(JSON.stringify(value))));
    }

    function decodeJson(value) {
      return JSON.parse(decodeURIComponent(escape(atob(value))));
    }

    function fileResponse(repoPath) {
      const value = files[repoPath];
      if (!value) {
        return null;
      }

      return {
        path: repoPath,
        type: "file",
        sha: "sha-" + repoPath,
        content: encodeJson(value)
      };
    }

    function listResponse(repoPath) {
      if (repoPath === ".macaroni/chats") {
        return [{ path: ".macaroni/chats/" + chatId, type: "dir", sha: "sha-chat" }];
      }

      if (repoPath === ".macaroni/chats/" + chatId + "/messages") {
        return [];
      }

      if (repoPath === ".macaroni/inbox/SA6E") {
        return [];
      }

      return null;
    }

    window.__macaroniWrites = [];
    window.__macaroniActivePut = false;
    window.fetch = (url, options = {}) => {
      const marker = "/contents/";
      const rawPath = String(url).slice(String(url).indexOf(marker) + marker.length).split("?")[0];
      const repoPath = decodeURIComponent(rawPath);

      if (options.method === "PUT") {
        if (window.__macaroniActivePut) {
          return Promise.resolve({
            ok: false,
            status: 409,
            statusText: "Conflict",
            text: () => Promise.resolve(JSON.stringify({ message: "parallel write conflict" }))
          });
        }

        window.__macaroniActivePut = true;
        const body = JSON.parse(options.body);
        const value = decodeJson(body.content);
        return new Promise((resolve) => {
          setTimeout(() => {
            files[repoPath] = value;
            window.__macaroniWrites.push({
              path: repoPath,
              message: body.message,
              value
            });
            window.__macaroniActivePut = false;
            resolve({
              ok: true,
              status: 200,
              statusText: "OK",
              text: () => Promise.resolve(JSON.stringify({ content: { path: repoPath, sha: "sha-written-" + repoPath } }))
            });
          }, 1000);
        });
      }

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
  await installProfile(page, { provider: "github", token: "fake-token-for-send-smoke" });
  await page.locator("#message-input").fill("Remote send hello");
  await page.locator("#message-input").press("Enter");
  await page.waitForFunction(() => [...document.querySelectorAll(".message-row .text")].some((node) => node.textContent.includes("Remote send hello")));
  const optimistic = await page.evaluate(() => ({
    input: document.querySelector("#message-input").value,
    writes: window.__macaroniWrites.length,
    status: document.querySelector("#sync-status").textContent
  }));
  assert(optimistic.input === "", "GitHub optimistic send did not clear composer immediately");
  assert(optimistic.writes === 0, "GitHub optimistic send waited for remote write before rendering");
  assert(optimistic.status.includes("background"), "GitHub optimistic send status did not show background send");
  await page.waitForFunction(() => document.querySelector("#sync-status").textContent.includes("send: ok"));

  const writes = await page.evaluate(() => window.__macaroniWrites);
  const messageWrite = writes.find((write) => /^\.macaroni\/chats\/chat_remote_send\/messages\/\d{4}\/\d{2}\/\d{2}\/.+\.json$/.test(write.path));
  const inboxWrite = writes.find((write) => /^\.macaroni\/inbox\/K2XM\/.+\.json$/.test(write.path));

  assert(messageWrite, "GitHub send did not write message file");
  assert(inboxWrite, "GitHub send did not write recipient inbox");
  assert(messageWrite.value.text === "Remote send hello", "GitHub message text is wrong");
  assert(messageWrite.value.from === "SA6E", "GitHub message author is wrong");
  assert(messageWrite.value.to.includes("K2XM"), "GitHub message recipient is wrong");
  assert(inboxWrite.value.message_path === messageWrite.path, "GitHub inbox notification does not point to message");

  await context.close();
}

async function testTwoClientRecipients(browser) {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "macaroni-mvp-smoke-"));
  const k2xmPath = path.join(tempDir, "messenger-k2xm.html");
  fs.writeFileSync(k2xmPath, fs.readFileSync(messengerPath, "utf8"));

  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await openMessenger(context, "file://" + k2xmPath, "K2XM");
  await installProfile(page, { clientId: "K2XM", displayName: "K2XM" });

  const members = await page.evaluate(() => window.MacaroniTestRepo.listFiles(".macaroni/chats/").then((files) => {
    const membersFile = files.find((file) => /members\.json$/.test(file.path));
    return membersFile ? JSON.parse(membersFile.content).members.map((member) => member.id) : [];
  }));
  assert(members.join(",") === "K2XM,SA6E", "K2XM default chat members are wrong: " + members.join(","));

  await page.locator("#message-input").fill("MVP smoke: K2XM to SA6E");
  await page.locator("#composer-form").evaluate((form) => form.requestSubmit());
  await page.waitForFunction(() => [...document.querySelectorAll(".message-row .text")].some((node) => node.textContent.includes("K2XM to SA6E")));

  const inboxFiles = await page.evaluate(() => window.MacaroniTestRepo.listFiles(".macaroni/inbox/").then((files) => files.map((file) => file.path)));
  assert(inboxFiles.some((file) => file.startsWith(".macaroni/inbox/SA6E/")), "K2XM did not write SA6E inbox");

  await context.close();
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    await testUnsupportedScreen(browser);
    await testGeneratedClientIdPersists(browser);
    await testPollingContract(browser);
    await testLanguageSettings(browser);
    await testLocalMvpFlow(browser);
    await testOutboxAndRetry(browser);
    await testGitHubRateLimitMessage(browser);
    await testGitHubInboxReindex(browser);
    await testGitHubSkipsUnchangedReindex(browser);
    await testGitHubReadOnlyMode(browser);
    await testGitHubSendWrites(browser);
    await testTwoClientRecipients(browser);
    console.log("MVP smoke passed");
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
