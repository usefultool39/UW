import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

const home = os.homedir()
const roots = [
  process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, 'Programs'),
  process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, 'Cocos'),
  process.env.APPDATA && path.join(process.env.APPDATA, 'Cocos'),
  process.env.ProgramData && path.join(process.env.ProgramData, 'cocos', 'editors'),
  process.env.PROGRAMFILES,
  process.env['ProgramFiles(x86)'],
  path.join(home, '.CocosCreator')
].filter(Boolean)

const dashboardCandidates = [
  process.env['ProgramFiles(x86)'] && path.join(process.env['ProgramFiles(x86)'], 'CocosDashboard', 'CocosDashboard.exe'),
  process.env.PROGRAMFILES && path.join(process.env.PROGRAMFILES, 'CocosDashboard', 'CocosDashboard.exe'),
  process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, 'Programs', 'CocosDashboard', 'CocosDashboard.exe')
].filter(Boolean)

const creatorNames = new Set(['CocosCreator.exe', 'Cocos Creator.exe'])

function exists(filePath) {
  try {
    return Boolean(filePath && fs.existsSync(filePath))
  } catch {
    return false
  }
}

function walkForExecutables(root, maxDepth = 5) {
  const found = []
  const seen = new Set()
  function visit(dir, depth) {
    if (!dir || depth > maxDepth || seen.has(dir)) return
    seen.add(dir)
    let entries
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true })
    } catch {
      return
    }
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name)
      if (entry.isFile() && creatorNames.has(entry.name)) found.push(fullPath)
      if (entry.isDirectory()) visit(fullPath, depth + 1)
    }
  }
  visit(root, 0)
  return found
}

const dashboard = dashboardCandidates.find(exists) || null
const creators = roots.flatMap((root) => walkForExecutables(root))
const uniqueCreators = [...new Set(creators)]
const hasProject = exists(path.join(process.cwd(), 'project.json'))
const hasTypes = exists(path.join(process.cwd(), 'node_modules', '@cocos', 'creator-types', 'engine.d.ts'))

const summary = {
  dashboard,
  creators: uniqueCreators,
  projectJson: hasProject,
  creatorTypes: hasTypes,
  recommendedCreator: 'Cocos Creator 3.8.x'
}

console.log(JSON.stringify(summary, null, 2))

if (!dashboard) {
  console.warn('Cocos Dashboard was not found. Install with: winget install --id Cocos.CocosDashboard --exact')
}
if (!uniqueCreators.length) {
  console.warn('Cocos Creator editor was not found yet. Open Cocos Dashboard and install a 3.8.x editor version, then open this folder as a project.')
}
if (!hasTypes) {
  console.warn('Cocos creator type declarations are missing. Run: npm install')
}
