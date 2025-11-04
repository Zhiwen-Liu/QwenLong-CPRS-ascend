import json
import requests
import time
import traceback

def compress_api_call_local_debug(messages: list, url='http://0.0.0.0:8091/qwen_long_compress_server'):
    """
    调试版压缩 API 调用，带详细计时和性能指标。
    返回: (result, elapsed_time_sec, input_char_count)
    """
    retry_cnt = 0
    max_retries = 2

    # 统计输入文本总长度（字符数，可近似代替 token）
    input_char_count = sum(len(msg.get('content', '')) for msg in messages)

    while retry_cnt < max_retries:
        try:
            data = {
                'header': {'request_id': "debug_test_timing"},
                'payload': {
                    'input': {'messages': messages},
                    'parameters': {
                        "min_keyword_len": 1,
                        "complete_sentence": False,
                        "batch_size": 1,
                        "chunk_size": 8192
                    }
                }
            }

            print(f"📊 Input size: {input_char_count} characters (~{input_char_count // 4} tokens est.)")
            print("🚀 Sending request to compression server...")

            start_time = time.time()  # ⏱️ 开始计时

            response = requests.post(url, json=data, timeout=120)  # 允许更长超时

            elapsed = time.time() - start_time  # ⏱️ 结束计时

            print(f"✅ Response received in {elapsed:.2f} seconds")
            print(f"Status Code: {response.status_code}")

            if response.status_code != 200:
                print(f"❌ HTTP Error: {response.text}")
                raise Exception(f"HTTP {response.status_code}")

            returns = response.json()
            output_text = returns['payload']['output']['text']

            # 性能指标
            output_char_count = len(''.join(output_text)) if isinstance(output_text, list) else len(output_text)
            compression_ratio = output_char_count / input_char_count if input_char_count > 0 else 0

            print(f"📈 Performance Metrics:")
            print(f"   - Input chars:  {input_char_count}")
            print(f"   - Output chars: {output_char_count}")
            print(f"   - Compression ratio: {compression_ratio:.2%}")
            print(f"   - Throughput: {input_char_count / elapsed:.0f} chars/sec")
            print(f"   - Latency: {elapsed:.2f} sec")

            return output_text, elapsed, input_char_count

        except Exception as e:
            elapsed = time.time() - start_time if 'start_time' in locals() else 0
            print(f"❌ Error after {elapsed:.2f} sec: {e}")
            traceback.print_exc()

        retry_cnt += 1
        if retry_cnt < max_retries:
            print(f"🔁 Retrying... ({retry_cnt}/{max_retries})")
            time.sleep(2)

    print("💥 All retries failed.")
    return [], -1, input_char_count


if __name__ == "__main__":
    # 构造测试数据
    test_query = "请总结文档中的核心观点和关键数据。"
    test_context = (
        "本文探讨了大语言模型在长文本处理中的挑战与优化策略。"
        "随着上下文窗口的扩展，模型面临计算资源消耗大、推理延迟高、信息冗余严重等问题。"
        "为解决这些问题，研究者提出了多种压缩与摘要技术，包括基于关键词提取、语义聚类、注意力机制剪枝等方法。"
        "实验表明，在保持问答准确率不低于95%的前提下，压缩模块可将平均上下文长度减少60%以上，显著提升系统吞吐量。"
        "\n\n此外，本文还分析了不同领域文档（如法律、医疗、科技）对压缩策略的敏感性，并提出了自适应压缩框架。"
    ) * 3  # 约 2000~3000 字

    messages_for_compress = [
        {'role': 'system', 'content': '你是一个高效的文档压缩器，请提炼关键信息，去除冗余。'},
        {'role': 'user', 'content': test_query},
        {'role': 'context', 'content': test_context}
    ]

    print("=" * 70)
    print("🧪 Starting compression service timing test...")
    print("=" * 70)

    result, latency, input_chars = compress_api_call_local_debug(messages_for_compress)
    print("result:", result)
    print("\n" + "=" * 70)
    if latency > 0:
        print(f"✅ SUCCESS | Latency: {latency:.2f}s | Input: {input_chars} chars")
    else:
        print("❌ FAILED | No valid response received.")
    print("=" * 70)
