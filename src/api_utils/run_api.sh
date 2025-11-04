export ASCEND_RT_VISIBLE_DEVICES="0,1" 
export MODEL_DIR="/data/models/QwenLong-CPRS-7B"
uvicorn run_api:app --port 8091 --host '0.0.0.0' --workers 1
