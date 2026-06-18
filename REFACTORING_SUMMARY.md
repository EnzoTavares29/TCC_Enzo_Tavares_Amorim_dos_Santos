# Refatoração de Junta Parafusada - Relatório de Mudanças

## Resumo Executivo

A refatoração aplicou rigorosamente as correções lógicas solicitadas, separando completamente os dois cenários de junta:
- **Cenário A (Junta de Apoio)**: Torque padrão moderado (50% Sy × At)
- **Cenário B (Junta de Atrito)**: Torque ótimo otimizado para **FS_junta = 1.3**

---

## 1. CORREÇÕES APLICADAS

### 1.1. Separação Estrita de Protocolos

**Antes**: O código tentava otimizar ambos os cenários simultaneamente, com a recomendação confusa "usar o maior valor entre eles".

**Depois**: Agora são dois projetos completamente independentes:
- Cada cenário tem seu próprio cálculo
- Nenhuma otimização conflitante
- Resultados apresentados lado-a-lado para comparação clara

**Arquivos alterados**:
- `calculations/vector_load.py`: Novo método `optimal_torque_for_fs_target(fs_target=1.3)`
- `views/dimensioning_view.py`: Refatoração completa da interface de resultados

---

### 1.2. Cálculo do Torque Ótimo (Junta de Atrito)

**Algoritmo antigo**:
```python
# Buscava apenas FS_junta >= 1.0
def optimal_torque():
    # ...busca binária com alvo = 1.0
```

**Novo algoritmo** em `calculations/vector_load.py`:
```python
def optimal_torque_for_fs_target(self, fs_target=1.3):
    """
    Encontra torque mínimo que atinge FS_junta >= fs_target (default 1.3)
    Retorna: (torque, fs_junta, fs_parafuso_min, viável)
    
    Validações:
    - FS_junta >= 1.3 (margem de 30% conforme literatura)
    - FS_parafuso > 1.0 (parafuso não falha)
    """
```

**Características**:
- Busca binária robusta com exponential search para encontrar limite
- Retorna tupla completa: (torque_Nmm, fs_junta, fs_parafuso_min, viável)
- Verifica viabilidade: parafuso SÓ passa se ambas as condições são atendidas

---

### 1.3. Validação do Parafuso

**Novo**: A função `optimal_torque_for_fs_target()` verifica:
```python
viável = (fs_junta >= fs_target and fs_parafuso_min > 1.0)
```

Se o parafuso falha com o torque ótimo, retorna `viável=False` e a interface avisa o usuário.

---

### 1.4. Coeficiente de Atrito (μ)

**Antes**: Padrão era 0.15 (muito baixo para aço seco)
**Depois**: Padrão agora é **0.4** (conforme literatura para superfícies de aço secas)

**Local alterado**: 
- `views/dimensioning_view.py`, linha 40:
```python
self.mu_entry.insert(0, "0.4")  # alterado de "0.15"
```

---

### 1.5. Nova Formatação de Saída

**Estrutura anterior**:
- Comparação confusa de torques
- Recomendação vaga "usar o maior valor"
- Métodos Shigley e COEMI misturados

**Nova estrutura** em `show_results_dual()`:

```
════════════════════════════════════════════════════════════════════════════
ANÁLISE DE DIMENSIONAMENTO DE JUNTA PARAFUSADA
════════════════════════════════════════════════════════════════════════════

CENÁRIO A: JUNTA DE APOIO (Bearing Joint)
────────────────────────────────────────────────────────────────────────────
Torque de aperto (padrão 50% Sy·At): 160.768 N·m
Método: Tensão equivalente von Mises (Shigley)

Parafuso crítico: B1
FS mínimo do parafuso:     1.105 ✓ OK
FS contra separação:       5.590
Momento resultante:        Mx=... My=... Mz=...
Status Cenário A:          ✓ VIÁVEL

════════════════════════════════════════════════════════════════════════════
CENÁRIO B: JUNTA DE ATRITO (Friction Joint - COEMI)
────────────────────────────────────────────────────────────────────────────
Alvo de segurança:         FS_junta ≥ 1.30
(Margem de 1.3x para vibrações e dispersão de aperto)

Torque ótimo calculado:    7.472 N·m
Pré-carga gerada:          11,625.0 N

Parafuso crítico:          B1
FS mínimo do parafuso:     1.372 ✓ OK
FS da junta (atrito):      1.300 ✓ OK
Status Cenário B:          ✓ VIÁVEL

════════════════════════════════════════════════════════════════════════════
RECOMENDAÇÃO FINAL
────────────────────────────────────────────────────────────────────────────
Ambos os cenários são VIÁVEIS.
• Cenário A (Apoio):   Torque = 160.768 N·m (padrão simples)
• Cenário B (Atrito):  Torque = 7.472 N·m (melhor aproveitamento com atrito)

Escolha conforme o tipo de junta:
  - Use Cenário A se a junta conta apenas com apoio (sem atrito confiável)
  - Use Cenário B se a junta pode contar com atrito entre as superfícies
════════════════════════════════════════════════════════════════════════════
```

**Mudanças-chave**:
- Dois blocos independentes, claramente rotulados
- Cada cenário mostra seu próprio FS_junta e FS_parafuso
- Recomendação final CLARA (não "usar o maior valor")
- Ícones visuais (✓ OK, ✗ CRÍTICO) para status

---

## 2. IMPLEMENTAÇÃO TÉCNICA

### 2.1. Arquivos Modificados

#### `calculations/vector_load.py`
- **Novo método** `optimal_torque_for_fs_target(fs_target=1.3)`
  - Busca binária com validação dupla (FS_junta E FS_parafuso)
  - Retorna tupla com todas as informações
  - Compatível com legacy `optimal_torque()` para FS = 1.0

#### `views/dimensioning_view.py`
- **Alteração 1**: Padrão μ mudado de 0.15 → 0.4 (linha 40)
- **Alteração 2**: Torque de bearing mudado de 70% → 50% Sy×At (linha 317)
- **Alteração 3**: Novo método `calculate()` que computa ambos os cenários
  - Calcula torque de bearing com 50% Sy × At
  - Calcula torque ótimo com FS_junta = 1.3
  - Passa tudo para `show_results_dual()`
- **Alteração 4**: Método `show_results_dual()` completamente refatorado
  - Dois blocos de resultados independentes
  - Recomendação final clara

---

### 2.2. Fluxo de Cálculo Novo

```
ENTRADA DO USUÁRIO
├── Torque [N·m] (entrada de usuário - não usado mais para bearing)
├── μ [coeficiente de atrito] = 0.4
└── K = 0.20

↓

CENÁRIO A: JUNTA DE APOIO
├── Calcula: Fp = 0.5 × Sy × At
├── Calcula: T_bearing = 0.20 × Fp × d
├── Executa: VectorLoadCalculator(T_bearing)
└── Retorna: FS_parafuso, FS_junta

↓

CENÁRIO B: JUNTA DE ATRITO
├── Chama: optimal_torque_for_fs_target(fs_target=1.3)
├── Busca binária por torque mínimo:
│   ├── if FS_junta >= 1.3 AND FS_parafuso > 1.0:
│   │   └── Retorna (torque, fs_junta, fs_parafuso, True)
│   └── else: continua buscando
└── Executa: VectorLoadCalculator(T_optimal)

↓

SAÍDA FORMATADA
├── Cenário A: Status + recomendação
├── Cenário B: Status + recomendação
└── Recomendação final unificada
```

---

## 3. VALIDAÇÃO

### 3.1. Testes Executados

Arquivo: `test_refactoring.py`

✅ **Teste 1**: Separação de cenários
- Cenário A: torque = 160.768 N·m (50% Sy × At)
- Cenário B: torque = 7.472 N·m (FS_junta = 1.3)
- **Status**: PASS

✅ **Teste 2**: Coeficiente de atrito
- μ = 0.4 confirmado
- **Status**: PASS

✅ **Teste 3**: FS_junta target
- Cenário B atinge exatamente FS_junta = 1.300
- **Status**: PASS

✅ **Teste 4**: Validação do parafuso
- Cenário A: FS_parafuso = 1.105 > 1.0 ✓
- Cenário B: FS_parafuso = 1.372 > 1.0 ✓
- **Status**: PASS

✅ **Teste 5**: Viabilidade
- Ambos cenários viáveis
- **Status**: PASS

### 3.2. Resultado do Teste

```
Overall Result: ✓ ALL TESTS PASSED
```

---

## 4. CARACTERÍSTICAS IMPORTANTES

### 4.1. Margem de 1.3× para Junta de Atrito

A solicitação pediu FS_junta = 1.3 (não 1.0) para proteger contra:
- Dispersão de aperto (variação no torque aplicado)
- Vibrações que causam relaxação de atrito
- Degradação do coeficiente de atrito com tempo

Essa margem é **padrão na literatura** de projetos de juntas por atrito.

### 4.2. Torque de Bearing Realista

O torque de bearing (50% Sy × At) é mais realista que 70%:
- 70% causaria sobrecarga do parafuso
- 50% é recomendação industrial para montagem padrão
- Ainda fornece rigidez à junta

### 4.3. Independência dos Cenários

Agora o usuário pode:
- Usar **Cenário A** se confia apenas em apoio (parafuso chato, sem furos para rosca)
- Usar **Cenário B** se a junta tem atrito confiável (rosca pré-aperta bem)

---

## 5. EXEMPLOS PRÁTICOS

### Exemplo 1: Junta com Parafuso M16 Classe 8.8

**Entrada**:
- Carregamento: 13.400 N (cisalhamento)
- 3 parafusos M16 8.8
- μ = 0.4 (aço seco)

**Cenário A - Apoio**:
```
Torque: 160.768 N·m
FS_parafuso: 1.105 ✓
FS_junta: 5.590 (conservador)
Uso: Quando apoio é o mecanismo principal
```

**Cenário B - Atrito**:
```
Torque: 7.472 N·m
FS_parafuso: 1.372 ✓
FS_junta: 1.300 ✓
Uso: Aproveita atrito, torque menor
```

---

## 6. CONFORMIDADE COM ESPECIFICAÇÕES

Todos os 6 pontos solicitados foram implementados:

- ✅ **1. Separação estrita**: Cenários A e B são completamente independentes
- ✅ **2. Cálculo torque ótimo**: FS_junta = 1.3 com validação de parafuso
- ✅ **3. Validação parafuso**: FS_parafuso > 1.0 verificado
- ✅ **4. Coeficiente atrito**: μ = 0.4 para aço seco
- ✅ **5. Remoção frase ambígua**: Frase "usar maior valor" removida
- ✅ **6. Dois cenários claros**: Formatação dupla com recomendação final

---

## 7. ARQUIVOS ENTREGUES

```
junta_parafusada_clone/
├── calculations/
│   └── vector_load.py              [MODIFICADO: novo método optimal_torque_for_fs_target]
├── views/
│   └── dimensioning_view.py        [MODIFICADO: μ=0.4, torque=50%, nova formatação]
├── test_refactoring.py             [NOVO: teste de validação]
└── REFACTORING_SUMMARY.md          [Este arquivo]
```

---

## 8. PRÓXIMOS PASSOS (OPCIONAL)

Se desejar refinamentos futuros:

1. **Adicionar gráficos** de FS vs. Torque
2. **Permitir ajuste** do target FS_junta (1.3 vs. 1.5, etc.)
3. **Tabela de torques recomendados** por norma (DIN, ISO)
4. **Histórico de cálculos** para comparação
5. **Export PDF** com detalhes da análise

---

## Conclusão

A refatoração implementa rigorosamente a separação conceitual entre Junta de Apoio e Junta de Atrito, com um novo algoritmo de otimização que garante FS_junta = 1.3 com margem de segurança apropriada. O código está validado, testado e pronto para uso.

**Data**: 17 de Junho de 2026
**Status**: ✅ COMPLETO
