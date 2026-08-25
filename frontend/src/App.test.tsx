import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it } from 'vitest'

import App from './App'

describe('App', () => {
  it('renders the M1 application shell', () => {
    const markup = renderToStaticMarkup(<App />)

    expect(markup).toContain('海龟汤')
    expect(markup).toContain('单人推理游戏')
  })
})
