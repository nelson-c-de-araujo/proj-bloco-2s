import os
import time
from typing import Dict, Any, Optional

"""
Módulo de Inferência Local com Large Language Models (LLM) via Hugging Face Transformers.
Modelo Selecionado: Qwen/Qwen2.5-0.5B-Instruct
Execução 100% local em CPU/GPU sem dependência de chaves de nuvem externas.
"""

MODEL_ID_PADRAO = os.getenv("LLM_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")

# Variáveis globais para padrão Singleton (Lazy Loading)
_MODELO = None
_TOKENIZER = None
_PIPELINE = None
_ERRO_INICIALIZACAO = None


def carregar_modelo_llm(model_id: str = MODEL_ID_PADRAO):
    """
    Inicializa sob demanda (Lazy Loading) o Tokenizer e o Modelo da Hugging Face
    armazenando em memória para reaproveitamento entre requisições.
    """
    global _MODELO, _TOKENIZER, _PIPELINE, _ERRO_INICIALIZACAO

    if _PIPELINE is not None:
        return _PIPELINE

    if _ERRO_INICIALIZACAO is not None:
        raise RuntimeError(_ERRO_INICIALIZACAO)

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

        print(f"[LLM Engine] Carregando modelo local da Hugging Face: {model_id}...")
        
        # Determina o dispositivo: usa GPU se disponível, senão CPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

        _TOKENIZER = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=True
        )

        _MODELO = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=dtype,
            device_map=device if device == "cuda" else None,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        )

        _PIPELINE = pipeline(
            "text-generation",
            model=_MODELO,
            tokenizer=_TOKENIZER,
            device=0 if device == "cuda" else -1
        )
        print(f"[LLM Engine] Modelo {model_id} carregado com sucesso no dispositivo: {device}!")
        return _PIPELINE

    except ImportError as e:
        _ERRO_INICIALIZACAO = (
            "Bibliotecas de IA local ('torch' ou 'transformers') não estão instaladas no ambiente. "
            "Execute 'pip install torch transformers accelerate' para habilitar a inferência local."
        )
        print(f"[LLM Engine Erro]: {_ERRO_INICIALIZACAO}")
        raise RuntimeError(_ERRO_INICIALIZACAO) from e
    except Exception as e:
        _ERRO_INICIALIZACAO = f"Falha ao carregar o modelo local da Hugging Face ({model_id}): {str(e)}"
        print(f"[LLM Engine Erro]: {_ERRO_INICIALIZACAO}")
        raise RuntimeError(_ERRO_INICIALIZACAO) from e


def construir_prompt_tarefa(tipo_analise: str, texto_entrada: str) -> list:
    """
    Formata o prompt no padrão ChatML instrucional para o Qwen2.5.
    """
    sistema = (
        "Você é um assistente especialista em emergência climática, sustentabilidade e no Objetivo de "
        "Desenvolvimento Sustentável 13 (Ação Contra a Mudança Global do Clima). "
        "Forneça respostas diretas, precisas e em português do Brasil."
    )

    if tipo_analise == "resumo":
        mensagem_usuario = (
            f"Elabore um resumo conciso (2 a 3 frases) destacando os pontos principais do seguinte texto:\n\n"
            f'"{texto_entrada}"'
        )
    elif tipo_analise == "sentimento":
        mensagem_usuario = (
            f"Analise o tom e impacto climático do seguinte texto sobre o ODS 13. "
            f"Classifique-o estritamente como POSITIVO (avanços, acordos, soluções), "
            f"NEGATIVO (alertas, secas, recordes de emissão, degradação) ou NEUTRO (informativo/técnico), "
            f"e forneça uma justificativa sucinta de uma frase:\n\n"
            f'"{texto_entrada}"'
        )
    elif tipo_analise == "insights":
        mensagem_usuario = (
            f"Apresente 2 ou 3 insights analíticos e implicações para a tomada de decisão socioambiental "
            f"a partir do texto abaixo:\n\n"
            f'"{texto_entrada}"'
        )
    else:
        mensagem_usuario = f"Processe e analise o texto a seguir no contexto do clima:\n\n\"{texto_entrada}\""

    return [
        {"role": "system", "content": sistema},
        {"role": "user", "content": mensagem_usuario}
    ]


def executar_processamento_texto(
    texto: str,
    tipo_analise: str = "resumo",
    max_novos_tokens: int = 150,
    temperatura: float = 0.7
) -> Dict[str, Any]:
    """
    Executa a tarefa de NLP solicitada sobre o texto fornecido utilizando o modelo local.
    Retorna o dicionário com o resultado e metadados de execução.
    """
    pipe = carregar_modelo_llm()
    
    mensagens = construir_prompt_tarefa(tipo_analise, texto)
    
    # Aplica o Chat Template nativo do modelo
    prompt_completo = _TOKENIZER.apply_chat_template(
        mensagens,
        tokenize=False,
        add_generation_prompt=True
    )

    inicio = time.time()
    
    respostas = pipe(
        prompt_completo,
        max_new_tokens=max_novos_tokens,
        temperature=max(0.1, min(temperatura, 1.0)),
        do_sample=temperatura > 0.1,
        top_p=0.9,
        pad_token_id=_TOKENIZER.eos_token_id
    )
    
    tempo_decorrido = round(time.time() - inicio, 3)
    
    texto_gerado = respostas[0]["generated_text"]
    # Extrai apenas a resposta gerada após o prompt de entrada
    if prompt_completo in texto_gerado:
        resposta_final = texto_gerado.replace(prompt_completo, "").strip()
    else:
        resposta_final = texto_gerado.strip()

    return {
        "resultado": resposta_final,
        "modelo": MODEL_ID_PADRAO,
        "tempo_execucao_segundos": tempo_decorrido,
        "tokens_gerados": len(_TOKENIZER.encode(resposta_final)) if _TOKENIZER else None
    }
