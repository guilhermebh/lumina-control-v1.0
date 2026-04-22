/**
 * Lumina Control - Business Intelligence Engine
 * Versão: 1.0
 * Descrição: Gerenciamento de estado e reatividade do Dashboard.
 */

// 1. Definição do Estado da Aplicação (Simulando persistência)
const LuminaState = {
    projetos: [
        { id: 1, valor: 4500, custo: 1200, origem: 'Instagram' },
        { id: 2, valor: 7200, custo: 1800, origem: 'Indicação' },
        { id: 3, valor: 3800, custo: 950, origem: 'Google Ads' }
    ],
    config: {
        moeda: 'BRL',
        taxaConversao: 1
    }
};

// 2. Funções de Cálculo (Lógica de Negócio no Frontend)
const CalculadoraBI = {
    getTicketMedio: () => {
        const total = LuminaState.projetos.reduce((acc, p) => acc + p.valor, 0);
        return (total / LuminaState.projetos.length) || 0;
    },

    getROIGlobal: () => {
        const receita = LuminaState.projetos.reduce((acc, p) => acc + p.valor, 0);
        const custos = LuminaState.projetos.reduce((acc, p) => acc + p.custo, 0);
        if (custos === 0) return 0;
        return ((receita - custos) / custos) * 100;
    }
};

// 3. Gerenciamento da Interface (DOM)
const UIController = {
    // Formatação de Moeda
    formatarMoeda: (valor) => {
        return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    },

    // Atualização dos Cards do Dashboard
    renderizarDashboard: () => {
        const ticketElement = document.getElementById('ticket-medio');
        const roiElement = document.getElementById('roi-total');
        const countElement = document.getElementById('projetos-contagem');

        // Aplicando os valores com animação simples de texto
        if (ticketElement) ticketElement.textContent = UIController.formatarMoeda(CalculadoraBI.getTicketMedio());
        if (roiElement) roiElement.textContent = `${CalculadoraBI.getROIGlobal().toFixed(1)}%`;
        if (countElement) countElement.textContent = LuminaState.projetos.length;

        console.log("Dashboard Lumina atualizado com sucesso.");
    },

    // Simulação de Fetch (Requisição ao Backend Python)
    sincronizarDados: async function() {
        const btn = document.querySelector('.btn-action');
        btn.textContent = "Sincronizando...";
        btn.disabled = true;

        // Simulando delay de rede/processamento de 1.5s
        await new Promise(resolve => setTimeout(resolve, 1500));

        this.renderizarDashboard();
        
        btn.textContent = "Sincronizar Dados";
        btn.disabled = false;
        
        // Feedback visual de sucesso
        alert("Dados do LuminaEngine integrados via SQLite com sucesso!");
    }
};

// 4. Inicialização do Sistema
document.addEventListener('DOMContentLoaded', () => {
    // Carregamento inicial
    UIController.renderizarDashboard();

    // Event Listeners
    const btnSync = document.querySelector('.btn-action');
    if (btnSync) {
        btnSync.addEventListener('click', () => {
            UIController.sincronizarDados();
        });
    }
});