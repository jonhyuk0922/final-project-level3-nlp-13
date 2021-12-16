from typing import *

import torch

from transformers import ElectraForSequenceClassification, AutoModelForSequenceClassification, AutoConfig, AutoTokenizer

'''
class_dict = {
    0: 'None',
    1: 'Hate',
    2: 'Hate',
}
'''

def get_model(model_kind:str, numlabels:int, model_name:str='beomi/KcELECTRA-base')->ElectraForSequenceClassification:
    '''모델 가져오기'''

    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    #model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)
    
    config = AutoConfig.from_pretrained(model_name)
    config.num_labels = numlabels
    model = ElectraForSequenceClassification(config=config)
    state_dicts = torch.load('./app/models/weights/' + model_kind)
    model.load_state_dict(state_dicts)
    model = model.to(device)
    
    return model

def get_tokenizer(model_name:str='beomi/KcELECTRA-base')->AutoTokenizer:
    '''토크나이져 가져오기'''

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return tokenizer

def predict_from_text(
    model: ElectraForSequenceClassification,
    tokenizer: AutoTokenizer,
    text: str) -> Union[int, float]:
    '''text를 받아 악성 댓글 여부를 판단하여 반환'''
    
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=50,
        add_special_tokens=True,
    )
    pred = model(input_ids = inputs['input_ids'].to(device))
    classes = torch.argmax(pred['logits'].detach()).detach().item()
    confidence = torch.max(pred['logits'].detach()).detach().item()
    return classes, confidence

def make_inference(
        text: str,
        model: AutoModelForSequenceClassification,
        tokenizer: AutoTokenizer
                     )->Union[int, float]:
    '''
        Arguments:
            - text: 유저의 채팅 내용
            - model: 악성 또는 감성 분석 모델
            - tokenizer: 악성 또는 감성 분석 모델의 토크나이저

        Returns:
            int, float

        Summary:
            유저의 채팅 내용, 모델, 토크나이저를 입력받아 모델에 따른 분석결과를 반환
    '''
    try:
        inference_result, confidence = predict_from_text(model=model, tokenizer=tokenizer, text=text)
    except:
        #raise HTTPException(status_code=404, detail=f"예측과정에서 오류가 발생했습니다. [text: {text}]")\
        print(f"예측과정에서 오류가 발생했습니다. [text: {text}]")

    return inference_result, confidence