--cria uma tabela para armazenar os dados diários
--"IF NOT EXISTS" evita erro se a tabela já existir 
CREATE TABLE IF NOT EXISTS weather_daily (

    --id gerado automaticamente para cada registro
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    --localizaçao representada pelos dados
    --"NOT NULL" significa que o campo é obrigatorio
    localidade TEXT NOT NULL,

    --identifica de onde os dados vieram
    fonte TEXT NOT NULL,

    --"DATE" armazena uma data, sem horario
    data DATE NOT NULL,

    --"NUMERIC(5, 1)" guarda ate cinco digitos no total, sendo um deles depois da virgula 
    --estes campos permitem NULL para representar dados ausentes 
    temperatura_maxima NUMERIC(5, 1),
    temperatura_minima NUMERIC(5, 1),

    --precipitação em milimetros, tambem permitindo valor ausente
    precipitacao NUMERIC(8, 2),

    --guarda o instante em que o registro foi inserido
    --"TIMESTAMPTZ" representa um instante com suporte a fuso horario
    --"DEFAULT CURRENT_TIMESTAMP" preenche automaticamente 
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    --impede dois registros da mesma localização, fonte e data
    CONSTRAINT weather_daily_localidade_fonte_data_unique
        UNIQUE (localidade, fonte, data),

    --impede precipitação negativa, mas permite NULL
    CONSTRAINT weather_daily_precipitacao_check
        CHECK (precipitacao >= 0),

    --quando as duas temperaturas existem, a máxima precisa ser maior ou igual a minima.
    CONSTRAINT weather_daily_temperaturas_check
        CHECK (temperatura_maxima >= temperatura_minima)
);