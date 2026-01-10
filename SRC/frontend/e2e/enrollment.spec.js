import { test, expect } from '@playwright/test'

test('E2E smoke: student login -> enroll -> see enrollment row', async ({ page }) => {
  await page.goto('/')
  await page.waitForURL('**/login')

  // default credentials already filled, but set explicit to be robust
  const inputs = page.locator('input')
  await inputs.nth(0).fill('student')
  await inputs.nth(1).fill('student123')
  await page.getByRole('button', { name: 'Login' }).click()

  await page.waitForURL('**/')
  await page.getByRole('link', { name: 'Enrollment' }).click()
  await page.waitForURL('**/enrollment')

  // Click first Enroll button
  const enrollBtn = page.getByRole('button', { name: 'Enroll' }).first()
  await enrollBtn.click()

  // Expect at least one row in My Enrollments
  await expect(page.getByText('My Enrollments')).toBeVisible()
  const rows = page.locator('table').nth(1).locator('tbody tr')
  await expect(rows).toHaveCount(1)
})
