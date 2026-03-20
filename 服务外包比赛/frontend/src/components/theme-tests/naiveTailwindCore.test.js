import { describe, expect, it } from 'vitest'
import {
  createIncrementId,
  canAddEdge,
  hasEdgeBetweenNodes,
  deleteEdge,
  deleteNodeAndRelatedEdges,
  normalizeEdgeStyle,
  pointsToPolylinePath,
  rectFromNodePosition,
  rectIntersectionArea,
  resolveDragCollision
} from './naiveTailwindCore'

describe('naiveTailwindCore', () => {
  it('新增-删除 100 次后不复用 ID，且历史节点集合保持不变', () => {
    const nodes = [{ id: 'N-1' }, { id: 'N-2' }, { id: 'N-3' }]
    const gen = createIncrementId('N-', 4)

    const created = new Set()
    const originalIds = nodes.map((n) => n.id)

    for (let i = 0; i < 100; i++) {
      const id = gen()
      created.add(id)
      nodes.push({ id })
      const idx = nodes.findIndex((n) => n.id === id)
      nodes.splice(idx, 1)
    }

    expect(created.size).toBe(100)
    expect(Array.from(created).at(0)).toBe('N-4')
    expect(Array.from(created).at(-1)).toBe('N-103')
    expect(nodes.map((n) => n.id)).toEqual(originalIds)
  })

  it('单线模式下：同向或反向边都视为冲突', () => {
    const edges = [{ id: 'E-1', source: 'A', target: 'B' }]
    expect(hasEdgeBetweenNodes(edges, 'A', 'B')).toBe(true)
    expect(hasEdgeBetweenNodes(edges, 'B', 'A')).toBe(true)
    expect(hasEdgeBetweenNodes(edges, 'A', 'C')).toBe(false)
    expect(canAddEdge(edges, 'A', 'B', { allowMultipleEdges: false })).toBe(false)
    expect(canAddEdge(edges, 'B', 'A', { allowMultipleEdges: false })).toBe(false)
  })

  it('多连线模式下：允许同向与反向重复连接', () => {
    const edges = [{ id: 'E-1', source: 'A', target: 'B' }]
    expect(canAddEdge(edges, 'A', 'B', { allowMultipleEdges: true })).toBe(true)
    expect(canAddEdge(edges, 'B', 'A', { allowMultipleEdges: true })).toBe(true)
  })

  it('拖拽碰撞消解后：移动节点与其它节点不重叠（含安全边距）', () => {
    const nodeWidth = 220
    const nodeHeight = 92
    const safePadding = 8
    const gridStep = 18
    const nodes = [
      { id: 'N-1', x: 100, y: 100 },
      { id: 'N-2', x: 360, y: 100 }
    ]

    const proposed = { x: 120, y: 110 }
    const bounds = { minX: 0, minY: 0, maxX: 1200, maxY: 900 }
    const res = resolveDragCollision({
      movingId: 'N-2',
      proposed,
      nodes,
      nodeWidth,
      nodeHeight,
      safePadding,
      gridStep,
      bounds
    })

    const a = rectFromNodePosition(nodes[0].x, nodes[0].y, nodeWidth, nodeHeight, safePadding)
    const b = rectFromNodePosition(res.x, res.y, nodeWidth, nodeHeight, safePadding)
    expect(rectIntersectionArea(a, b)).toBe(0)
  })

  it('删除节点：同时删除关联连线', () => {
    const nodes = [{ id: 'A' }, { id: 'B' }, { id: 'C' }]
    const edges = [
      { id: 'E1', source: 'A', target: 'B' },
      { id: 'E2', source: 'B', target: 'C' },
      { id: 'E3', source: 'C', target: 'A' }
    ]
    const res = deleteNodeAndRelatedEdges(nodes, edges, 'B')
    expect(res.nodes.map((n) => n.id)).toEqual(['A', 'C'])
    expect(res.edges.map((e) => e.id)).toEqual(['E3'])
  })

  it('删除连线：仅移除指定 id', () => {
    const edges = [{ id: 'E1' }, { id: 'E2' }, { id: 'E3' }]
    expect(deleteEdge(edges, 'E2').map((e) => e.id)).toEqual(['E1', 'E3'])
  })

  it('连线样式归一化：不允许虚线/形状等字段，仅保留颜色与线宽（默认加粗）', () => {
    expect(normalizeEdgeStyle(undefined)).toEqual({ color: '#22d3ee', width: 4 })
    expect(normalizeEdgeStyle({ color: '#000', width: 6, pattern: 'dashed', shape: 'bezier' })).toEqual({ color: '#000', width: 6 })
    expect(normalizeEdgeStyle({ color: '#000', width: 'not-number' })).toEqual({ color: '#000', width: 4 })
  })

  it('折线 path 仅由直线段组成（无 Q/C 曲线）', () => {
    const d = pointsToPolylinePath([
      { x: 0, y: 0 },
      { x: 10, y: 0 },
      { x: 10, y: 20 }
    ])
    expect(d.includes('Q')).toBe(false)
    expect(d.includes('C')).toBe(false)
    expect(d).toBe('M 0 0 L 10 0 L 10 20')
  })

  it('折线 path 强制正交：遇到对角点自动插入拐点', () => {
    const d = pointsToPolylinePath([
      { x: 0, y: 0 },
      { x: 10, y: 20 }
    ])
    expect(d).toBe('M 0 0 L 10 0 L 10 20')
  })
})
