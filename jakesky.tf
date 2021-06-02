# Sourced from environment variables named TF_VAR_${VAR_NAME}
variable "aws_acct_id" {}

variable "jakesky_darksky_key" {}

variable "jakesky_geocodio_key" {}

variable "jakesky_skill_id" {}

variable "jakesky_latitude" {}

variable "jakesky_longitude" {}

variable "jakesky_filename" {
  type    = string
  default = "JakeSky.zip"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

provider "aws" {
  region = var.aws_region
}

resource "aws_cloudwatch_event_rule" "jakesky_schedule" {
  name                = "jakesky-schedule"
  description         = "Run jakesky periodically to keep the Lambda warmed"
  schedule_expression = "cron(0/5 11_13 ? * * *)"
}

resource "aws_kms_key" "lambda_default_key" {
  enable_key_rotation = "true"
}

data "aws_iam_policy_document" "jakesky_role_policy_document" {
  statement {
    actions   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents", "logs:Describe*"]
    resources = ["arn:aws:logs:${var.aws_region}:${var.aws_acct_id}:*"]
  }
}

data "aws_iam_policy_document" "jakesky_assume_role_policy_document" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_policy" "jakesky_role_policy" {
  name   = "jakesky"
  policy = data.aws_iam_policy_document.jakesky_role_policy_document.json
}

resource "aws_iam_role" "jakesky_role" {
  name               = "jakesky"
  assume_role_policy = data.aws_iam_policy_document.jakesky_assume_role_policy_document.json
}

resource "aws_iam_role_policy_attachment" "jakesky_role_attachment" {
  role       = aws_iam_role.jakesky_role.name
  policy_arn = aws_iam_policy.jakesky_role_policy.arn
}

resource "aws_lambda_function" "jakesky" {
  filename         = var.jakesky_filename
  function_name    = "jakesky"
  role             = aws_iam_role.jakesky_role.arn
  handler          = "jakesky.alexa_handler"
  source_code_hash = filebase64sha256(var.jakesky_filename)
  runtime          = "python3.8"
  publish          = "false"
  description      = "Retrieve local weather from DarkSky for commutes and lunchtime"

  kms_key_arn = aws_kms_key.lambda_default_key.arn
  environment {
    variables = {
      JAKESKY_DARKSKY_KEY  = var.jakesky_darksky_key
      JAKESKY_GEOCODIO_KEY = var.jakesky_geocodio_key
      JAKESKY_SKILL_ID     = var.jakesky_skill_id
      JAKESKY_LATITUDE     = var.jakesky_latitude
      JAKESKY_LONGITUDE    = var.jakesky_longitude
    }
  }
}

resource "aws_cloudwatch_log_group" "jakesky_logs" {
  name              = "/aws/lambda/jakesky"
  retention_in_days = "7"
}

