/**
 * 知识图谱可视化组件
 * 使用Cytoscape.js进行可视化
 */

class KnowledgeGraphVisualizer {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            height: options.height || 600,
            layout: options.layout || 'cose',
            ...options
        };
        this.cy = null;
        this.currentNodes = [];
        this.currentEdges = [];
    }

    async initialize() {
        // 加载Cytoscape.js
        if (typeof cytoscape === 'undefined') {
            await this.loadCytoscape();
        }
        
        this.cy = cytoscape({
            container: document.getElementById(this.containerId),
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': '#619B8A',
                        'label': 'data(label)',
                        'width': 50,
                        'height': 50,
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'color': '#fff',
                        'font-size': '12px',
                        'font-weight': 'bold',
                        'border-width': 2,
                        'border-color': '#fff',
                        'shape': 'ellipse'
                    }
                },
                {
                    selector: 'node[type="纸浆产品"]',
                    style: {
                        'background-color': '#F77F00'
                    }
                },
                {
                    selector: 'node[type="生产企业"]',
                    style: {
                        'background-color': '#FCBF49'
                    }
                },
                {
                    selector: 'node[type="原材料"]',
                    style: {
                        'background-color': '#EAE2B7'
                    }
                },
                {
                    selector: 'node[type="化学助剂"]',
                    style: {
                        'background-color': '#D62828'
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 3,
                        'line-color': '#ccc',
                        'target-arrow-color': '#ccc',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': 'data(label)',
                        'font-size': '10px',
                        'text-rotation': 'autorotate',
                        'text-margin-y': -10
                    }
                }
            ],
            layout: {
                name: this.options.layout,
                padding: 30
            }
        });

        // 添加交互
        this.setupInteractions();
    }

    async loadCytoscape() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/cytoscape@3.26.0/dist/cytoscape.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    setupInteractions() {
        // 点击节点显示详情
        this.cy.on('tap', 'node', (evt) => {
            const node = evt.target;
            this.showNodeDetails(node);
        });

        // 悬停显示工具提示
        this.cy.on('mouseover', 'node', (evt) => {
            const node = evt.target;
            const label = node.data('label');
            const type = node.data('type');
            this.showTooltip(label + ' (' + type + ')');
        });

        this.cy.on('mouseout', 'node', () => {
            this.hideTooltip();
        });
    }

    async loadData(entityNames) {
        try {
            const response = await fetch('/api/kg/visualize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(entityNames)
            });

            const data = await response.json();
            
            if (data.success) {
                this.render(data.data);
                return data;
            } else {
                throw new Error('Failed to load data');
            }
        } catch (error) {
            console.error('Error loading data:', error);
            throw error;
        }
    }

    render(visData) {
        const elements = [];
        
        // 添加节点
        visData.nodes.forEach(node => {
            elements.push({
                data: {
                    id: node.id,
                    label: node.label,
                    type: node.type,
                    group: node.group,
                    level: node.level,
                    attributes: node.attributes
                }
            });
        });
        
        // 添加边
        visData.edges.forEach(edge => {
            elements.push({
                data: {
                    id: `${edge.from}-${edge.to}`,
                    source: edge.from,
                    target: edge.to,
                    label: edge.label,
                    type: edge.type
                }
            });
        });
        
        this.cy.elements().remove();
        this.cy.add(elements);
        
        this.currentNodes = visData.nodes;
        this.currentEdges = visData.edges;
        
        // 自动适应布局
        this.cy.layout({ name: this.options.layout, padding: 30 }).run();
    }

    showNodeDetails(node) {
        const nodeData = node.data();
        
        // 创建详情弹窗
        const modal = document.createElement('div');
        modal.className = 'kg-node-details-modal';
        modal.innerHTML = `
            <div class="kg-modal-content">
                <span class="kg-modal-close">&times;</span>
                <h3>${nodeData.label}</h3>
                <p><strong>类型：</strong>${nodeData.type}</p>
                ${nodeData.attributes ? `
                    <div>
                        <strong>属性：</strong>
                        <ul>
                            ${Object.entries(nodeData.attributes).map(([k, v]) => 
                                `<li>${k}: ${v}</li>`
                            ).join('')}
                        </ul>
                    </div>
                ` : ''}
                <button onclick="loadRelatedEntities('${nodeData.id}')">查看关联实体</button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 关闭按钮
        modal.querySelector('.kg-modal-close').onclick = () => {
            modal.remove();
        };
    }

    showTooltip(text) {
        let tooltip = document.getElementById('kg-tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'kg-tooltip';
            document.body.appendChild(tooltip);
        }
        tooltip.textContent = text;
        tooltip.style.display = 'block';
    }

    hideTooltip() {
        const tooltip = document.getElementById('kg-tooltip');
        if (tooltip) {
            tooltip.style.display = 'none';
        }
    }

    exportImage() {
        const png = this.cy.png({ scale: 2 });
        const link = document.createElement('a');
        link.download = 'knowledge_graph.png';
        link.href = png;
        link.click();
    }

    exportJSON() {
        const json = this.cy.json();
        const dataStr = JSON.stringify(json, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'knowledge_graph.json';
        link.click();
    }
}

// 使用示例
async function visualizeKnowledgeGraph(entityNames, containerId = 'kg-visualization') {
    const visualizer = new KnowledgeGraphVisualizer(containerId);
    await visualizer.initialize();
    await visualizer.loadData(entityNames);
    return visualizer;
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KnowledgeGraphVisualizer;
}

