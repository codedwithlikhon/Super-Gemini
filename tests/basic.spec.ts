import { test, expect } from '@playwright/test';

test('basic test', async ({ page }) => {
  await page.goto('/');
  const title = page.locator('h1');
  await expect(title).toContainText('Super-Gemini');
});

test('navigation links', async ({ page }) => {
  await page.goto('/');
  
  // Test Documentation links
  const docsLinks = page.locator('a[href^="docs/"]');
  await expect(docsLinks).toHaveCount(3); // installation.md, usage.md, roadmap.md

  // Test Quick Links
  const quickLinks = page.locator('a[href*="github.com"]');
  await expect(quickLinks).toHaveCount(2); // Issues and New Issue links
});

test('mobile responsiveness', async ({ page }) => {
  await page.goto('/');
  
  // Test mobile viewport
  await page.setViewportSize({ width: 375, height: 667 });
  
  // Check if content is visible and properly formatted
  await expect(page.locator('div.ascii-art')).toBeVisible();
  await expect(page.locator('h2')).toBeVisible();
});

test('features section', async ({ page }) => {
  await page.goto('/');
  
  // Test all feature sections are present
  const featureSections = [
    '🤖 Local-First AI Agent Execution',
    '🔄 Multi-Runtime Support',
    '🏗️ Web Application Scaffolding',
    '📱 Android/Termux Integration',
    '🧠 Persistent Memory Management',
    '🧪 Comprehensive Testing'
  ];

  for (const section of featureSections) {
    await expect(page.locator('h3', { hasText: section })).toBeVisible();
  }
});