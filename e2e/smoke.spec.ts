import { test, expect } from '@playwright/test'

test('homepage loads and shows title', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('text=PMP Super Mock')).toBeVisible()
})

test('language toggle switches to Chinese', async ({ page }) => {
  await page.goto('/')
  await page.click('text=繁中')
  await expect(page.locator('text=PMP 超級模擬')).toBeVisible()
})

test('navigation works', async ({ page }) => {
  await page.goto('/')
  await page.click('text=Practice')
  await expect(page).toHaveURL('/mode')
})
