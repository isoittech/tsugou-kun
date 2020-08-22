CREATE TABLE IF NOT EXISTS fx_learn_data(
  Datetime timestamp with time zone NOT NULL
  , TimeLabel INTEGER NOT NULL
  , WeekDay INTEGER NOT NULL
  , Open DOUBLE NOT NULL
  , High DOUBLE NOT NULL
  , Low DOUBLE NOT NULL
  , Close DOUBLE NOT NULL
  , UwahigePip DOUBLE NOT NULL
  , ShitahigePip DOUBLE NOT NULL
  , DoutaiPip DOUBLE NOT NULL
  , Inyou INTEGER NOT NULL
  , UwahigeDiffPip DOUBLE NOT NULL
  , ShitahigeDiffPip DOUBLE NOT NULL
  , DoutaiDiffPip DOUBLE NOT NULL
  , Close_Diff_3 DOUBLE NOT NULL
  , Close_Diff_6 DOUBLE NOT NULL
  , Close_Diff_9 DOUBLE NOT NULL
  , Close_Diff_12 DOUBLE NOT NULL
  , Close_Diff_15 DOUBLE NOT NULL
  , Close_Diff_18 DOUBLE NOT NULL
  , Close_Diff_Class_3 INTEGER NOT NULL
  , Close_Diff_Class_6 INTEGER NOT NULL
  , Close_Diff_Class_9 INTEGER NOT NULL
  , Close_Diff_Class_12 INTEGER NOT NULL
  , Close_Diff_Class_15 INTEGER NOT NULL
  , Close_Diff_Class_18 INTEGER NOT NULL
  , PRIMARY KEY (Datetime)
);
 